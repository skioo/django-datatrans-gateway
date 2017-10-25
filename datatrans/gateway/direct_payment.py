from collections import namedtuple
from moneyed import Money

from .money_xml_helpers import money_to_amount_and_currency
from ..config import sign_web, web_merchant_id

PaymentParameters = namedtuple('PaymentParameters', 'merchant_id amount currency refno sign')


def build_payment_parameters(amount: Money, client_ref: str) -> PaymentParameters:
    """
    Builds the parameters needed to present the user with a datatrans payment form.

    :param amount: The amount and currency we want the user to pay
    :param client_ref: A unique reference for this payment
    :return: The parameters needed to display the datatrans payment form
    """
    merchant_id = web_merchant_id
    amount, currency = money_to_amount_and_currency(amount)
    refno = client_ref
    sign = sign_web(merchant_id, amount, currency, refno)
    return PaymentParameters(
        merchant_id=merchant_id,
        amount=amount,
        currency=currency,
        refno=refno,
        sign=sign
    )
