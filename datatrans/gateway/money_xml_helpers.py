from xml.etree.ElementTree import Element

from moneyed import Money
from typing import Tuple


def value_to_amount_and_currency(value: Money) -> Tuple[int, str]:
    amount = int(value.amount * 100)
    currency_code = value.currency.code
    return amount, currency_code


def parse_money(e: Element) -> Money:
    return Money(
        amount=int(e.find('amount').text) / 100,
        currency=e.find('currency').text
    )
