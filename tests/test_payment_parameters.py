from django.test import TestCase
from moneyed import Money

from datatrans.gateway import PaymentParameters, build_payment_parameters, build_register_credit_card_parameters


class PaymentTest(TestCase):
    def test_it_should_generate_payment_parameters(self):
        parameters = build_payment_parameters(amount=Money(8.50, 'CHF'), client_ref='91827364')
        expected = PaymentParameters(
            merchant_id='1111111111',
            amount=850,
            currency='CHF',
            refno='91827364',
            sign='afdd2eef36dd6f39222ee6c3bb641c9731817508068f3e807c21adb3fe483d04',
            use_alias=False,
        )
        assert parameters == expected


class RegisterCreditCardTest(TestCase):
    def test_it_should_generate_register_credit_card_parameters(self):
        parameters = build_register_credit_card_parameters(client_ref='someref')
        expected = PaymentParameters(
            merchant_id='1111111111',
            amount=0,
            currency='CHF',
            refno='someref',
            sign='dc638f47b56f05130c6437f67b637919e294e6e06e44fad9f2e517ff2e8683c4',
            use_alias=True,
        )
        assert parameters == expected
