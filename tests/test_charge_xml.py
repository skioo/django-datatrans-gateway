from django.test import TestCase
from moneyed import Money

from datatrans.gateway import build_charge_request_xml, parse_charge_response_xml
from datatrans.models import Charge, AliasRegistration
from .utils import assertModelEqual


class BuildChargeTest(TestCase):
    def test_build_request(self):
        xml = build_charge_request_xml(
            value=Money(123, "CHF"),
            client_ref='abcdef',
            alias_registration=AliasRegistration(
                transaction_id='170707111922838874',
                merchant_id='2222222222',
                request_type='CAA',
                masked_card_number='424242xxxxxx4242',
                card_alias='70119122433810042',
                expiry_month=12,
                expiry_year=18,
                client_ref='1234',
                value=Money(123, 'CHF'),
                payment_method='VIS',
                credit_card_country='CHE',
                authorization_code='953988933',
                acquirer_authorization_code='111953',
                response_code='01',
                response_message='check successful',
            )
        )
        expected = """<?xml version='1.0' encoding='utf8'?>
<authorizationService version="3"><body merchantId="2222222222"><transaction refno="abcdef"><request><amount>12300</amount><currency>CHF</currency><aliasCC>70119122433810042</aliasCC><expm>12</expm><expy>18</expy><reqtype>CAA</reqtype><sign>4c1324f4708a8b07310b47089a0041724b0155067e0ffb37ceb3b00d3a24d067</sign></request></transaction></body></authorizationService>"""  # noqa
        self.assertEqual(expected, xml.decode())


class ParseChargeTest(TestCase):
    def test_success(self):
        response = """<?xml version='1.0' encoding='utf8'?>
<authorizationService version='3'>
  <body merchantId='2222222222' status='accepted'>
    <transaction refno='1234' trxStatus='response'>
      <request>
        <amount>1000</amount>
        <currency>CHF</currency>
        <aliasCC>70119122433810042</aliasCC>
        <expm>12</expm>
        <expy>18</expy>
        <reqtype>CAA</reqtype>
        <sign>redacted</sign>
      </request>
      <response>
        <responseCode>01</responseCode>
        <responseMessage>Authorized</responseMessage>
        <uppTransactionId>170717104749732144</uppTransactionId>
        <authorizationCode>749762145</authorizationCode>
        <acqAuthorizationCode>104749</acqAuthorizationCode>
        <maskedCC>424242xxxxxx4242</maskedCC>
        <returnCustomerCountry>CHE</returnCustomerCountry>
      </response>
    </transaction>
  </body>
</authorizationService>"""
        expected = Charge(
            is_success=True,
            transaction_id='170717104749732144',
            merchant_id='2222222222',
            request_type='CAA',
            masked_card_number='424242xxxxxx4242',
            card_alias='70119122433810042',
            expiry_month=12,
            expiry_year=18,
            client_ref='1234',
            value=Money(10, 'CHF'),
            credit_card_country='CHE',
            response_code='01',
            response_message='Authorized',
            authorization_code='749762145',
            acquirer_authorization_code='104749',
        )
        assertModelEqual(self, expected, parse_charge_response_xml(response))

    def test_declined(self):
        response = """<?xml version='1.0' encoding='utf8'?>
<authorizationService version='3'>
  <body merchantId='2222222222' status='accepted'>
    <transaction refno='1234' trxStatus='error'>
      <request>
        <amount>9900</amount>
        <currency>CHF</currency>
        <aliasCC>70119122433810042</aliasCC>
        <expm>12</expm>
        <expy>18</expy>
        <reqtype>CAA</reqtype>
        <sign>redacted</sign>
      </request>
      <error>
        <errorCode>1403</errorCode>
        <errorMessage>declined</errorMessage>
        <errorDetail>Declined</errorDetail>
        <uppTransactionId>170718174305765364</uppTransactionId>
        <acqErrorCode>50</acqErrorCode>
        <returnCustomerCountry>CHE</returnCustomerCountry>
      </error>
    </transaction>
  </body>
</authorizationService>"""
        expected = Charge(
            is_success=False,
            transaction_id='170718174305765364',
            merchant_id='2222222222',
            request_type='CAA',
            card_alias='70119122433810042',
            expiry_month=12,
            expiry_year=18,
            client_ref='1234',
            value=Money(99, 'CHF'),
            credit_card_country='CHE',
            error_code='1403',
            error_message='declined',
            error_detail='Declined',
            acquirer_error_code='50',
        )
        assertModelEqual(self, expected, parse_charge_response_xml(response))

    def test_no_acquirer_for_currency(self):
        response = """<?xml version='1.0' encoding='utf8'?>
<authorizationService version='3'>
  <body merchantId='2222222222' status='accepted'>
    <transaction refno='1234' trxStatus='error'>
      <request>
        <amount>11100</amount>
        <currency>RUB</currency>
        <aliasCC>70119122433810042</aliasCC>
        <expm>12</expm>
        <expy>18</expy>
        <reqtype>CAA</reqtype>
        <sign>redacted</sign>
      </request>
      <error>
        <errorCode>1009</errorCode>
        <errorMessage>payment acquirer does not exist</errorMessage>
        <errorDetail>VIS/RUB</errorDetail>
        <uppTransactionId>170718193544941457</uppTransactionId>
        <returnCustomerCountry>CHE</returnCustomerCountry>
      </error>
    </transaction>
  </body>
</authorizationService>"""
        expected = Charge(
            is_success=False,
            transaction_id='170718193544941457',
            merchant_id='2222222222',
            request_type='CAA',
            card_alias='70119122433810042',
            expiry_month=12,
            expiry_year=18,
            client_ref='1234',
            value=Money(111, 'RUB'),
            credit_card_country='CHE',
            error_code='1009',
            error_message='payment acquirer does not exist',
            error_detail='VIS/RUB',
        )
        assertModelEqual(self, expected, parse_charge_response_xml(response))
