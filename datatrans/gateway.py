from xml.etree.ElementTree import Element, SubElement, tostring

import requests
from collections import namedtuple
from defusedxml.ElementTree import fromstring
from moneyed import Money
from structlog import get_logger
from typing import Union, Tuple

from .config import datatrans_authorize_url, sign_mpo, mpo_merchant_id, web_merchant_id, sign_web
from .models import AliasRegistration, Charge, Payment
from .signals import charge_done, alias_registration_done, payment_done

logger = get_logger()

PaymentParameters = namedtuple('PaymentParameters', 'merchant_id amount currency refno sign')


def charge(value: Money, client_ref: str, alias_registration_id: str) -> Charge:
    """
    Charges money using datatrans, given a previously registered card alias.

    :param value: The amount and currency we want to charge
    :param client_ref: A unique reference for this charge
    :param alias_registration:
    :return: Either a Charge or a ChargeError
    """
    alias_registration = AliasRegistration.objects.get(pk=alias_registration_id)

    logger.info('charging-credit-card', value=value, client_ref=client_ref,
                alias_registration=alias_registration)
    request_xml = build_charge_request_xml(value, client_ref, alias_registration)
    response = requests.post(
        url=datatrans_authorize_url,
        headers={'Content-Type': 'application/xml'},
        data=request_xml,
    )
    charge_response = parse_charge_response_xml(response.content)
    logger.debug('processing-charge-response', charge_response=charge_response)
    process_event(charge_response)
    return charge_response


def build_payment_parameters(value: Money, client_ref: str) -> PaymentParameters:
    """
    Builds the parameters needed to present the user with a datatrans payment form.

    :param value: The amount and currency we want the user to pay
    :param client_ref: A unique reference for this payment
    :return: The parameters needed to display the datatrans payment form
    """
    merchant_id = web_merchant_id
    amount, currency = value_to_amount_and_currency(value)
    refno = client_ref
    sign = sign_web(merchant_id, amount, currency, refno)
    return PaymentParameters(
        merchant_id=merchant_id,
        amount=amount,
        currency=currency,
        refno=refno,
        sign=sign
    )


# Internals


def handle_notification(xml: str) -> None:
    notification = parse_notification_xml(xml)
    logger.debug('processing-notification', notification=notification)
    process_event(notification)


def process_event(o: Union[Payment, AliasRegistration, Charge]) -> None:
    """
    Save object and then notify signals
    """
    o.save()

    if isinstance(o, Payment):
        signal = payment_done
        log_message = 'signalling-payment-done'
    elif isinstance(o, AliasRegistration):
        signal = alias_registration_done
        log_message = 'signalling-alias-registration-done'
    elif isinstance(o, Charge):
        signal = charge_done
        log_message = 'signalling-charge-done'
    else:
        raise ValueError("Unknown event type")

    logger.debug(log_message, is_success=o.is_success, client_ref=o.client_ref)
    # send_robust hides exceptions, so we use send, just like the rest of django
    signal.send(sender=None, instance=o, is_success=o.is_success, client_ref=o.client_ref)


def value_to_amount_and_currency(value: Money) -> Tuple[int, str]:
    amount = int(value.amount * 100)
    currency_code = value.currency.code
    return amount, currency_code


def parse_money(e: Element) -> Money:
    return Money(
        amount=int(e.find('amount').text) / 100,
        currency=e.find('currency').text
    )


def parse_notification_xml(xml: str) -> Union[AliasRegistration, Payment]:
    """"
    Both alias registration and payments are received here.
    We can differentiate them by looking at the use-alias user-parameter (and verifying the amount is o).

    """
    body = fromstring(xml).find('body')
    transaction = body.find('transaction')
    _user_parameters = transaction.find('userParameters')

    def get_named_parameter(name):
        return _user_parameters.find("parameter[@name='" + name + "']")

    def is_success():
        return transaction.get('status') == 'success'

    def parse_success():
        # From the spec: sign2 is only returned in the success case
        computed_signature = sign_web(body.get('merchantId'), transaction.find('amount').text,
                                      transaction.find('currency').text,
                                      transaction.find('uppTransactionId').text)

        sign2 = get_named_parameter('sign2').text
        if computed_signature != sign2:
            raise ValueError('sign2 did not match computed signature')

        success = transaction.find('success')
        return dict(
            response_code=success.find('responseCode').text,
            response_message=success.find('responseMessage').text,
            authorization_code=success.find('authorizationCode').text,
            acquirer_authorization_code=success.find('acqAuthorizationCode').text,
        )

    def parse_error():
        error = transaction.find('error')
        return dict(
            error_code=error.find('errorCode').text,
            error_message=error.find('errorMessage').text,
            error_detail=error.find('errorDetail').text,
            acquirer_error_code=get_named_parameter('acqErrorCode').text,
        )

    def parse_common_attributes():
        return dict(
            transaction_id=transaction.find('uppTransactionId').text,
            merchant_id=body.get('merchantId'),
            request_type=transaction.find('reqtype').text,
            expiry_month=int(get_named_parameter('expm').text),
            expiry_year=int(get_named_parameter('expy').text),
            client_ref=transaction.get('refno'),
            value=parse_money(transaction),
            payment_method=transaction.find('pmethod').text,
            credit_card_country=get_named_parameter('returnCustomerCountry').text,
        )

    use_alias_parameter = get_named_parameter('useAlias')
    if use_alias_parameter is not None and use_alias_parameter.text == 'true':

        register_alias_attributes = dict(
            masked_card_number=get_named_parameter('maskedCC').text,
            card_alias=get_named_parameter('aliasCC').text,
        )

        if is_success():
            d = dict(is_success=True)
            d.update(register_alias_attributes)
            d.update(parse_common_attributes())
            d.update(parse_success())
            return AliasRegistration(**d)
        else:
            d = dict(is_success=False)
            d.update(register_alias_attributes)
            d.update(parse_common_attributes())
            d.update(parse_error())
            return AliasRegistration(**d)
    else:
        if is_success():
            d = dict(
                is_success=True,
                masked_card_number=get_named_parameter('cardno').text
            )
            d.update(parse_common_attributes())
            d.update(parse_success())
            return Payment(**d)
        else:
            d = dict(is_success=False)
            d.update(parse_common_attributes())
            d.update(parse_error())
            return Payment(**d)


def build_charge_request_xml(value: Money, client_ref: str, alias_registration: AliasRegistration) -> bytes:
    merchant_id = mpo_merchant_id
    client_ref = client_ref

    root = Element('authorizationService')
    root.set('version', '3')

    body = SubElement(root, 'body')
    body.set('merchantId', merchant_id)

    transaction = SubElement(body, 'transaction')
    transaction.set('refno', client_ref)

    request = SubElement(transaction, 'request')

    amount, currency = value_to_amount_and_currency(value)
    SubElement(request, 'amount').text = str(amount)
    SubElement(request, 'currency').text = currency
    SubElement(request, 'aliasCC').text = alias_registration.card_alias
    SubElement(request, 'expm').text = str(alias_registration.expiry_month)
    SubElement(request, 'expy').text = str(alias_registration.expiry_year)
    SubElement(request, 'reqtype').text = 'CAA'
    SubElement(request, 'sign').text = sign_mpo(merchant_id, amount, currency, client_ref)

    return tostring(root, encoding='utf8')


def parse_charge_response_xml(xml: bytes) -> Charge:
    body = fromstring(xml).find('body')
    status = body.get('status')
    transaction = body.find('transaction')
    trxStatus = transaction.get('trxStatus')
    request = transaction.find('request')

    common_attributes = dict(
        merchant_id=body.get('merchantId'),
        card_alias=request.find('aliasCC').text,
        expiry_month=int(request.find('expm').text),
        expiry_year=int(request.find('expy').text),
        request_type=request.find('reqtype').text,
        client_ref=transaction.get('refno'),
        value=parse_money(request)
    )

    if status == 'accepted' and trxStatus == 'response':
        response = transaction.find('response')

        transaction_id = response.find('uppTransactionId').text
        masked_card_number = response.find('maskedCC').text
        return_customer_country = response.find('returnCustomerCountry').text

        response_code = response.find('responseCode').text
        response_message = response.find('responseMessage').text
        authorization_code = response.find('authorizationCode').text
        acquirer_authorization_code = response.find('acqAuthorizationCode').text

        d = dict(
            is_success=True,
            transaction_id=transaction_id,
            masked_card_number=masked_card_number,
            credit_card_country=return_customer_country,
            response_code=response_code,
            response_message=response_message,
            authorization_code=authorization_code,
            acquirer_authorization_code=acquirer_authorization_code,
        )
        d.update(common_attributes)
        return Charge(**d)
    else:
        error = transaction.find('error')

        acquirer_error_code_element = error.find('acqErrorCode')

        d = dict(
            is_success=False,
            error_code=error.find('errorCode').text,
            error_message=error.find('errorMessage').text,
            error_detail=error.find('errorDetail').text,
            acquirer_error_code=acquirer_error_code_element.text if acquirer_error_code_element is not None else '',
            transaction_id=error.find('uppTransactionId').text,
            credit_card_country=error.find('returnCustomerCountry').text,
        )
        d.update(**common_attributes)
        return Charge(**d)
