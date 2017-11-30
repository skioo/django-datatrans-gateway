from datetime import date

from django.test import TestCase
from moneyed import Money

from datatrans.models import AliasRegistration, Payment, Refund


class AliasRegistrationModelTest(TestCase):
    def test_expiry_date(self):
        alias_registration = AliasRegistration(
            success=True,
            transaction_id='170707111922838874',
            merchant_id='1111111111',
            request_type='CAA',
            masked_card_number='424242xxxxxx4242',
            card_alias='70119122433810042',
            expiry_month=12,
            expiry_year=18,
            client_ref='1234',
            amount=Money(0, 'CHF'),
            payment_method='VIS',
            credit_card_country='CHE',
            authorization_code='953988933',
            acquirer_authorization_code='111953',
            response_code='01',
            response_message='check successful',
        )
        alias_registration.full_clean()
        alias_registration.save()
        assert alias_registration.expiry_date == date(2018, 12, 31)

    def test_minimal_fields(self):
        alias_registration = AliasRegistration(
            success=False,
            transaction_id='170710155947695609',
            merchant_id='1111111111',
            request_type='CAA',
            expiry_month=11,
            expiry_year=19,
            client_ref='1234',
            amount=Money(0, 'CHF'),
            payment_method='ECA',
            error_code='1403',
            error_message='declined',
            error_detail='card declined in test mode',
        )
        alias_registration.full_clean()
        alias_registration.save()


class PaymentModelTest(TestCase):
    def test_pointspay(self):
        """
        A pointspay payment does not have a masked credit card, nor expiry, nor customer country.
        """
        payment = Payment(
            success=True,
            transaction_id='170707111922838874',
            merchant_id='1111111111',
            request_type='CAA',
            client_ref='1234',
            amount=Money(0, 'CHF'),
            payment_method='PPA',
            credit_card_country='CHE',
            authorization_code='953988933',
            acquirer_authorization_code='111953',
            response_code='01',
            response_message='PPA transaction OK',
        )
        payment.full_clean()
        payment.save()

    def test_payment_in_unsupported_currency(self):
        """
        This payment failure has a very few attributes, verify we are able to store it.
        """
        payment = Payment(
            success=False,
            transaction_id='170802095839802669',
            merchant_id='1111111111',
            client_ref='5',
            amount=Money(5, 'CHF'),
            payment_method='VIS',
            error_code='-999',
            error_message='without error message',
            error_detail='not available payment method',
        )
        payment.full_clean()
        payment.save()


class RefundModelTest(TestCase):
    def test_save_successful_refund(self):
        refund = Refund(
            success=True,
            transaction_id='171015120225118036',
            merchant_id='1111111111',
            request_type='COA',
            payment_transaction_id='170803184046388845',
            client_ref='1234-r',
            amount=Money(1, 'CHF'),
            response_code='01',
            response_message='credit succeeded',
            authorization_code='225128037',
            acquirer_authorization_code='120225',
        )
        refund.full_clean()
        refund.save()

    def test_save_errored_refund(self):
        """
        An errored refund doesn't have a transaction id, make sure we can store it anyways.
        """
        refund = Refund(
            success=False,
            merchant_id='1111111111',
            request_type='COA',
            payment_transaction_id='170803184046388845',
            client_ref='1234-r',
            amount=Money(1, 'CHF'),
            error_code='2000',
            error_message='access denied',
            error_detail='incorrect merchantId',
        )
        refund.full_clean()
        refund.save()

    def test_save_many_errored_refund(self):
        """
        Transaction id is unique and can be empty. Make sure that more than one empty
        transaction id can co-exist in the database.
        """
        refund1 = Refund(
            success=False,
            merchant_id='1111111111',
            request_type='COA',
            payment_transaction_id='170803184046388845',
            client_ref='1234-r',
            amount=Money(1, 'CHF'),
            error_code='2000',
            error_message='access denied',
            error_detail='incorrect merchantId',
        )
        refund1.save()

        refund2 = Refund(
            success=False,
            merchant_id='1111111111',
            request_type='COA',
            payment_transaction_id='170803184046388845',
            client_ref='5678-r',
            amount=Money(2, 'CHF'),
            error_code='2000',
            error_message='access denied',
            error_detail='incorrect merchantId',
        )
        refund2.save()
