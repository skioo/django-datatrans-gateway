from collections import namedtuple

from moneyed import Money
from structlog import get_logger

from .money_xml_converters import money_to_amount_and_currency
from ..config import sign_web, web_merchant_id

logger = get_logger()

PaymentParameters = namedtuple('PaymentParameters', 'merchant_id amount currency refno sign use_alias')


def build_payment_parameters(amount: Money, client_ref: str) -> PaymentParameters:
    """
    Builds the parameters needed to present the user with a datatrans payment form.

    :param amount: The amount and currency we want the user to pay
    :param client_ref: A unique reference for this payment
    :return: The parameters needed to display the datatrans form
    """
    merchant_id = web_merchant_id
    amount, currency = money_to_amount_and_currency(amount)
    refno = client_ref
    sign = sign_web(merchant_id, amount, currency, refno)

    parameters = PaymentParameters(
        merchant_id=merchant_id,
        amount=amount,
        currency=currency,
        refno=refno,
        sign=sign,
        use_alias=False,
    )

    logger.info('build-payment-parameters', parameters=parameters)

    return parameters


def build_register_credit_card_parameters(client_ref: str) -> PaymentParameters:
    """
    Builds the parameters needed to present the user with a datatrans form to register a credit card.
    Contrary to a payment form, datatrans will not show an amount.

    :param client_ref: A unique reference for this alias capture.
    :return: The parameters needed to display the datatrans form
    """

    amount = 0
    currency = 'CHF'  # Datatrans requires this value to be filled, so we use this arbitrary currency.
    merchant_id = web_merchant_id
    refno = client_ref
    sign = sign_web(merchant_id, amount, currency, refno)

    parameters = PaymentParameters(
        merchant_id=merchant_id,
        amount=amount,
        currency=currency,
        refno=refno,
        sign=sign,
        use_alias=True,
    )

    logger.info('building-payment-parameters', parameters=parameters)

    return parameters
