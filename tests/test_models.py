from datetime import date

from django.test import TestCase
from moneyed import Money

from datatrans.models import AliasRegistration


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
        self.assertEqual(date(2018, 12, 31), aliasRegistration.expiry_date)
