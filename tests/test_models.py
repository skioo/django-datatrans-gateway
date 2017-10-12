from datetime import date

from django.test import TestCase
from moneyed import Money

from datatrans.models import AliasRegistration, Payment


class AliasRegistrationModelTest(TestCase):
    def test_expiry_date(self):
        aliasRegistration = AliasRegistration(
            is_success=True,
            transaction_id='170707111922838874',
            merchant_id='1111111111',
            request_type='CAA',
            masked_card_number='424242xxxxxx4242',
            card_alias='70119122433810042',
            expiry_month=12,
            expiry_year=18,
            client_ref='1234',
            value=Money(0, 'CHF'),
            payment_method='VIS',
            credit_card_country='CHE',
            authorization_code='953988933',
            acquirer_authorization_code='111953',
            response_code='01',
            response_message='check successful',
        )
        aliasRegistration.save()
        assert aliasRegistration.expiry_date == date(2018, 12, 31)


class PaymentModelTest(TestCase):
    def test_pointspay(self):
        """
        A pointspay payment does not have a masked credit card, nor expiry, nor customer country.
        """
        payment = Payment(
            is_success=True,
            transaction_id='170707111922838874',
            merchant_id='1111111111',
            request_type='CAA',
            client_ref='1234',
            value=Money(0, 'CHF'),
            payment_method='PPA',
            credit_card_country='CHE',
            authorization_code='953988933',
            acquirer_authorization_code='111953',
            response_code='01',
            response_message='PPA transaction OK',
        )
        payment.save()

    def test_payment_in_unsupported_currency(self):
        """
        This payment failure has a very few attributes, verify we are able to store it.
        """
        payment = Payment(
            is_success=False,
            transaction_id='170802095839802669',
            merchant_id='1111111111',
            client_ref='5',
            value=Money(5, 'CHF'),
            payment_method='VIS',
            error_code='-999',
            error_message='without error message',
            error_detail='not available payment method',
        )
        payment.save()
