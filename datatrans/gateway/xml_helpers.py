from decimal import Decimal
from xml.etree.ElementTree import Element

from moneyed import Money
from typing import Tuple


def money_to_amount_and_currency(money: Money) -> Tuple[int, str]:
    amount = int(money.amount * 100)
    currency_code = money.currency.code
    return amount, currency_code


def parse_money(e: Element) -> Money:
    return Money(
        amount=Decimal(e.find('amount').text) / 100,
        currency=e.find('currency').text
    )
