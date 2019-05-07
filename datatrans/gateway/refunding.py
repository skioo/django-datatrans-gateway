from xml.etree.ElementTree import Element, SubElement, tostring

import requests
from defusedxml.ElementTree import fromstring
from moneyed import Money
from structlog import get_logger

from .money_xml_converters import money_to_amount_and_currency, parse_money
from ..config import datatrans_processor_url, sign_web
from ..models import Payment, Refund

logger = get_logger()


def refund(amount: Money, payment_id: str) -> Refund:
    """
    Refunds (partially or completely) a previously authorized and settled payment.
    :param amount: The amount and currency we want to refund. Must be positive, in the same currency
    as the original payment, and not exceed the amount of the original payment.
    :param payment_id: The id of the payment to refund.
    :return: a Refund (either successful or not).
    """
    if amount.amount <= 0:
        raise ValueError('Refund takes a strictly positive amount')
    payment = Payment.objects.get(pk=payment_id)
    if not payment.success:
        raise ValueError('Only successful payments can be refunded')
    if payment.amount.currency != amount.currency:
        raise ValueError('Refund currency must be identical to original payment currency')
    if amount.amount > payment.amount.amount:
        raise ValueError('Refund amount exceeds original payment amount')

    logger.info('refunding-payment', amount=str(amount),
                payment=dict(amount=str(payment.amount), transaction_id=payment.transaction_id,
                             masked_card_number=payment.masked_card_number))

    client_ref = '{}-r'.format(payment.client_ref)

    request_xml = build_refund_request_xml(amount=amount,
                                           original_transaction_id=payment.transaction_id,
                                           client_ref=client_ref,
                                           merchant_id=payment.merchant_id)

    logger.info('sending-refund-request', url=datatrans_processor_url, data=request_xml)

    response = requests.post(
        url=datatrans_processor_url,
        headers={'Content-Type': 'application/xml'},
        data=request_xml)

    logger.info('processing-refund-response', response=response.content)

    refund_response = parse_refund_response_xml(response.content)
    refund_response.save()
    refund_response.send_signal()

    return refund_response


def build_refund_request_xml(amount: Money, client_ref: str, original_transaction_id: str, merchant_id: str) -> bytes:
    client_ref = client_ref

    root = Element('paymentService')
    root.set('version', '1')

    body = SubElement(root, 'body')
    body.set('merchantId', merchant_id)

    transaction = SubElement(body, 'transaction')
    transaction.set('refno', client_ref)

    request = SubElement(transaction, 'request')

    amount, currency = money_to_amount_and_currency(amount)
    SubElement(request, 'amount').text = str(amount)
    SubElement(request, 'currency').text = currency
    SubElement(request, 'uppTransactionId').text = original_transaction_id
    SubElement(request, 'transtype').text = '06'
    SubElement(request, 'sign').text = sign_web(merchant_id, amount, currency, client_ref)

    return tostring(root, encoding='utf8')


def parse_refund_response_xml(xml: bytes) -> Refund:
    body = fromstring(xml).find('body')
    status = body.get('status')
    transaction = body.find('transaction')
    trx_status = transaction.get('trxStatus')
    request = transaction.find('request')

    common_attributes = dict(
        merchant_id=body.get('merchantId'),
        client_ref=transaction.get('refno'),
        amount=parse_money(request),
        payment_transaction_id=request.find('uppTransactionId').text,
    )

    request_type = request.find('reqtype')
    if request_type is not None:
        common_attributes['request_type'] = request_type.text

    if status == 'accepted' and trx_status == 'response':
        response = transaction.find('response')

        transaction_id = response.find('uppTransactionId').text
        response_code = response.find('responseCode').text
        response_message = response.find('responseMessage').text
        authorization_code = response.find('authorizationCode').text
        acquirer_authorization_code = response.find('acqAuthorizationCode').text

        d = dict(
            success=True,
            transaction_id=transaction_id,
            response_code=response_code,
            response_message=response_message,
            authorization_code=authorization_code,
            acquirer_authorization_code=acquirer_authorization_code,
        )
        d.update(common_attributes)
        return Refund(**d)
    else:
        error = transaction.find('error')

        acquirer_error_code_element = error.find('acqErrorCode')

        d = dict(
            success=False,
            error_code=error.find('errorCode').text,
            error_message=error.find('errorMessage').text,
            error_detail=error.find('errorDetail').text,
            acquirer_error_code=acquirer_error_code_element.text if acquirer_error_code_element is not None else '',
        )
        d.update(**common_attributes)
        return Refund(**d)
