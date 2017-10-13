from xml.etree.ElementTree import Element, SubElement, tostring

from defusedxml.ElementTree import fromstring
from moneyed import Money
import requests
from structlog import get_logger

from .money_xml_helpers import parse_money, value_to_amount_and_currency
from ..config import datatrans_authorize_url, mpo_merchant_id, sign_mpo
from ..models import AliasRegistration, Payment

logger = get_logger()


def charge(value: Money, client_ref: str, alias_registration_id: str) -> Payment:
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
    charge_response.save()

    charge_response.send_signal()

    return charge_response


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


def parse_charge_response_xml(xml: bytes) -> Payment:
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
        return Payment(**d)
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
        return Payment(**d)
