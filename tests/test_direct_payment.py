from django.test import TestCase
from moneyed import Money

from datatrans.gateway import PaymentParameters, build_payment_parameters


class DirectPaymentTest(TestCase):
    def test_it_should_generate_payment_parameters(self):
        payment_parameters = build_payment_parameters(amount=Money(8.50, 'CHF'), client_ref='91827364')
        expected = PaymentParameters(
            merchant_id='1111111111',
            amount=850,
            currency='CHF',
            refno='91827364',
            sign='afdd2eef36dd6f39222ee6c3bb641c9731817508068f3e807c21adb3fe483d04',
        )
        assert payment_parameters == expected
