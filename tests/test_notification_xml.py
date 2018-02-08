from django.test import TestCase
from moneyed import Money

from datatrans.gateway.notification import parse_notification_xml
from datatrans.models import AliasRegistration, Payment
from .utils import assertModelEqual


class ParseRegisterAliasTest(TestCase):
    def test_success(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<uppTransactionService version="1">
  <body merchantId="1111111111" testOnly="yes">
    <transaction refno="b0ca4cf0-7955-4eb3-978b-936194c8fe23" status="success">
      <uppTransactionId>170707111922838874</uppTransactionId>
      <amount>0</amount>
      <currency>CHF</currency>
      <pmethod>VIS</pmethod>
      <reqtype>CAA</reqtype>
      <success>
        <authorizationCode>953988933</authorizationCode>
        <acqAuthorizationCode>111953</acqAuthorizationCode>
        <responseMessage>check successful</responseMessage>
        <responseCode>01</responseCode>
      </success>
      <userParameters>
        <parameter name="maskedCC">424242xxxxxx4242</parameter>
        <parameter name="sign">redacted</parameter>
        <parameter name="aliasCC">70119122433810042</parameter>
        <parameter name="responseCode">01</parameter>
        <parameter name="mode">lightbox</parameter>
        <parameter name="sign2">6b8f6adfe37bf8ab331e7576563395647c59350270b4d38b60aa4903f9018030</parameter>
        <parameter name="expy">18</parameter>
        <parameter name="returnCustomerCountry">CHE</parameter>
        <parameter name="theme">DT2015</parameter>
        <parameter name="uppReturnTarget">_top</parameter>
        <parameter name="expm">12</parameter>
        <parameter name="version">1.0.2</parameter>
        <parameter name="cardno">424242xxxxxx4242</parameter>
        <parameter name="useAlias">true</parameter>
      </userParameters>
    </transaction>
  </body>
</uppTransactionService>
    """
        expected = AliasRegistration(
            success=True,
            transaction_id='170707111922838874',
            merchant_id='1111111111',
            request_type='CAA',
            masked_card_number='424242xxxxxx4242',
            card_alias='70119122433810042',
            expiry_month=12,
            expiry_year=18,
            client_ref='b0ca4cf0-7955-4eb3-978b-936194c8fe23',
            amount=Money(0, 'CHF'),
            payment_method='VIS',
            credit_card_country='CHE',
            response_code='01',
            response_message='check successful',
            authorization_code='953988933',
            acquirer_authorization_code='111953',
        )
        parsed = parse_notification_xml(xml)
        assertModelEqual(expected, parsed)

    def test_empty_response_code(self):
        """ This happens with myone cards."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<uppTransactionService version="1">
  <body merchantId="1111111111" testOnly="yes">
    <transaction refno="b0ca4cf0-7955-4eb3-978b-936194c8fe23" status="success">
      <uppTransactionId>170707111922838874</uppTransactionId>
      <amount>0</amount>
      <currency>CHF</currency>
      <pmethod>VIS</pmethod>
      <reqtype>CAA</reqtype>
      <success>
        <authorizationCode>953988933</authorizationCode>
        <acqAuthorizationCode>111953</acqAuthorizationCode>
        <responseMessage>check successful</responseMessage>
        <responseCode></responseCode>
      </success>
      <userParameters>
        <parameter name="maskedCC">424242xxxxxx4242</parameter>
        <parameter name="sign">redacted</parameter>
        <parameter name="aliasCC">70119122433810042</parameter>
        <parameter name="responseCode">01</parameter>
        <parameter name="mode">lightbox</parameter>
        <parameter name="sign2">6b8f6adfe37bf8ab331e7576563395647c59350270b4d38b60aa4903f9018030</parameter>
        <parameter name="expy">18</parameter>
        <parameter name="returnCustomerCountry">CHE</parameter>
        <parameter name="theme">DT2015</parameter>
        <parameter name="uppReturnTarget">_top</parameter>
        <parameter name="expm">12</parameter>
        <parameter name="version">1.0.2</parameter>
        <parameter name="cardno">424242xxxxxx4242</parameter>
        <parameter name="useAlias">true</parameter>
      </userParameters>
    </transaction>
  </body>
</uppTransactionService>
        """

        expected = AliasRegistration(
            success=True,
            transaction_id='170707111922838874',
            merchant_id='1111111111',
            request_type='CAA',
            masked_card_number='424242xxxxxx4242',
            card_alias='70119122433810042',
            expiry_month=12,
            expiry_year=18,
            client_ref='b0ca4cf0-7955-4eb3-978b-936194c8fe23',
            amount=Money(0, 'CHF'),
            payment_method='VIS',
            credit_card_country='CHE',
            response_message='check successful',
            authorization_code='953988933',
            acquirer_authorization_code='111953',
        )
        parsed = parse_notification_xml(xml)
        assertModelEqual(expected, parsed)

    def test_wrong_sign2(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<uppTransactionService version="1">
  <body merchantId="1111111111" testOnly="yes">
    <transaction refno="1234" status="success">
      <uppTransactionId>170707111922838874</uppTransactionId>
      <amount>0</amount>
      <currency>CHF</currency>
      <pmethod>VIS</pmethod>
      <reqtype>CAA</reqtype>
      <success>
        <authorizationCode>953988933</authorizationCode>
        <acqAuthorizationCode>111953</acqAuthorizationCode>
        <responseMessage>check successful</responseMessage>
        <responseCode>01</responseCode>
      </success>
      <userParameters>
        <parameter name="maskedCC">424242xxxxxx4242</parameter>
        <parameter name="sign">redacted</parameter>
        <parameter name="aliasCC">70119122433810042</parameter>
        <parameter name="responseCode">01</parameter>
        <parameter name="mode">lightbox</parameter>
        <parameter name="sign2">somethingcompletelydifferent</parameter>
        <parameter name="expy">18</parameter>
        <parameter name="returnCustomerCountry">CHE</parameter>
        <parameter name="theme">DT2015</parameter>
        <parameter name="uppReturnTarget">_top</parameter>
        <parameter name="expm">12</parameter>
        <parameter name="version">1.0.2</parameter>
        <parameter name="cardno">424242xxxxxx4242</parameter>
        <parameter name="useAlias">true</parameter>
      </userParameters>
    </transaction>
  </body>
</uppTransactionService>
    """
        with self.assertRaises(ValueError):
            parse_notification_xml(xml)

    def test_wrong_expiry_date(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<uppTransactionService version="1">
  <body merchantId="1111111111" testOnly="yes">
    <transaction refno="1234" status="error">
      <uppTransactionId>170710155947695609</uppTransactionId>
      <amount>0</amount>
      <currency>CHF</currency>
      <pmethod>VIS</pmethod>
      <reqtype>CAA</reqtype>
      <error>
        <errorCode>1403</errorCode>
        <errorMessage>declined</errorMessage>
        <errorDetail>Declined</errorDetail>
      </error>
      <userParameters>
        <parameter name="maskedCC">424242xxxxxx4242</parameter>
        <parameter name="sign">redacted</parameter>
        <parameter name="aliasCC">70119122433810042</parameter>
        <parameter name="version">1.0.2</parameter>
        <parameter name="mode">lightbox</parameter>
        <parameter name="expy">18</parameter>
        <parameter name="returnCustomerCountry">CHE</parameter>
        <parameter name="theme">DT2015</parameter>
        <parameter name="acqErrorCode">50</parameter>
        <parameter name="uppReturnTarget">_top</parameter>
        <parameter name="expm">11</parameter>
        <parameter name="useAlias">true</parameter>
      </userParameters>
    </transaction>
  </body>
</uppTransactionService>
        """
        expected = AliasRegistration(
            success=False,
            transaction_id='170710155947695609',
            merchant_id='1111111111',
            request_type='CAA',
            masked_card_number='424242xxxxxx4242',
            card_alias='70119122433810042',
            expiry_month=11,
            expiry_year=18,
            client_ref='1234',
            amount=Money(0, 'CHF'),
            payment_method='VIS',
            credit_card_country='CHE',

            error_code='1403',
            error_message='declined',
            error_detail='Declined',
            acquirer_error_code='50',
        )
        parsed = parse_notification_xml(xml)
        assertModelEqual(expected, parsed)

    def test_card_number_and_alias_are_not_always_present(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<uppTransactionService version="1">
  <body merchantId="1111111111" testOnly="yes">
    <transaction refno="1234" status="error">
      <uppTransactionId>170710155947695609</uppTransactionId>
      <amount>0</amount>
      <currency>CHF</currency>
      <pmethod>ECA</pmethod>
      <reqtype>CAA</reqtype>
      <language>no</language>
      <error>
        <errorCode>1403</errorCode>
        <errorMessage>declined</errorMessage>
        <errorDetail>card declined in test mode</errorDetail>
      </error>
      <userParameters>
        <parameter name="sign">redacted</parameter>
        <parameter name="expy">19</parameter>
        <parameter name="uppWebResponseMethod">GET</parameter>
        <parameter name="theme">DT2015</parameter>
        <parameter name="expm">11</parameter>
        <parameter name="useAlias">true</parameter>
      </userParameters>
    </transaction>
  </body>
</uppTransactionService>
        """
        expected = AliasRegistration(
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
            error_detail='card declined in test mode')
        parsed = parse_notification_xml(xml)
        assertModelEqual(expected, parsed)


class ParsePaymentTest(TestCase):
    def test_success(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<uppTransactionService version="1">
  <body merchantId="1111111111" testOnly="yes">
    <transaction refno="1234" status="success">
      <uppTransactionId>170719094930353253</uppTransactionId>
      <amount>100</amount>
      <currency>CHF</currency>
      <pmethod>ECA</pmethod>
      <reqtype>CAA</reqtype>
      <success>
        <authorizationCode>957923350</authorizationCode>
        <acqAuthorizationCode>094957</acqAuthorizationCode>
        <responseMessage>Authorized</responseMessage>
        <responseCode>01</responseCode>
      </success>
      <userParameters>
        <parameter name="sign">redacted</parameter>
        <parameter name="responseCode">01</parameter>
        <parameter name="mode">lightbox</parameter>
        <parameter name="sign2">d67901cd33853a68239786b6d08e97e7cb3deecce430591ceabe6924fb25e450</parameter>
        <parameter name="expy">18</parameter>
        <parameter name="returnCustomerCountry">MYS</parameter>
        <parameter name="theme">DT2015</parameter>
        <parameter name="uppReturnTarget">_top</parameter>
        <parameter name="expm">12</parameter>
        <parameter name="cardno">520000xxxxxx0007</parameter>
        <parameter name="version">1.0.2</parameter>
      </userParameters>
    </transaction>
  </body>
</uppTransactionService>
        """
        expected = Payment(
            success=True,
            transaction_id='170719094930353253',
            merchant_id='1111111111',
            request_type='CAA',
            masked_card_number='520000xxxxxx0007',
            expiry_month=12,
            expiry_year=18,
            client_ref='1234',
            amount=Money(1.0, 'CHF'),
            payment_method='ECA',
            credit_card_country='MYS',
            response_code='01',
            response_message='Authorized',
            authorization_code='957923350',
            acquirer_authorization_code='094957',
        )
        parsed = parse_notification_xml(xml)
        assertModelEqual(expected, parsed)

    def test_use_alias_present_but_empty(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<uppTransactionService version="1">
  <body merchantId="1111111111" testOnly="yes">
    <transaction refno="1" status="success">
      <uppTransactionId>170721140542657759</uppTransactionId>
      <amount>100</amount>
      <currency>CHF</currency>
      <pmethod>VIS</pmethod>
      <reqtype>CAA</reqtype>
      <success>
        <authorizationCode>554797791</authorizationCode>
        <acqAuthorizationCode>140554</acqAuthorizationCode>
        <responseMessage>Authorized</responseMessage>
        <responseCode>01</responseCode>
      </success>
      <userParameters>
        <parameter name="sign">redacted</parameter>
        <parameter name="responseCode">01</parameter>
        <parameter name="mode">lightbox</parameter>
        <parameter name="sign2">4c261378c8872844984bc71c9feebbe9ec7ec4df445c268bfa2abfd0e68d78e0</parameter>
        <parameter name="expy">18</parameter>
        <parameter name="returnCustomerCountry">CHE</parameter>
        <parameter name="theme">DT2015</parameter>
        <parameter name="uppReturnTarget">_top</parameter>
        <parameter name="expm">12</parameter>
        <parameter name="cardno">424242xxxxxx4242</parameter>
        <parameter name="version">1.0.2</parameter>
        <parameter name="useAlias"></parameter>
      </userParameters>
    </transaction>
  </body>
</uppTransactionService>"""
        expected = Payment(
            success=True,
            transaction_id='170721140542657759',
            merchant_id='1111111111',
            request_type='CAA',
            masked_card_number='424242xxxxxx4242',
            expiry_month=12,
            expiry_year=18,
            client_ref='1',
            amount=Money(1.0, 'CHF'),
            payment_method='VIS',
            credit_card_country='CHE',
            response_code='01',
            response_message='Authorized',
            authorization_code='554797791',
            acquirer_authorization_code='140554',
        )
        parsed = parse_notification_xml(xml)
        assertModelEqual(expected, parsed)

    def test_wrong_expiry(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<uppTransactionService version="1">
  <body merchantId="1111111111" testOnly="yes">
    <transaction refno="1234" status="error">
      <uppTransactionId>170720154219033737</uppTransactionId>
      <amount>100</amount>
      <currency>CHF</currency>
      <pmethod>VIS</pmethod>
      <reqtype>CAA</reqtype>
      <error>
        <errorCode>1403</errorCode>
        <errorMessage>declined</errorMessage>
        <errorDetail>Declined</errorDetail>
      </error>
      <userParameters>
        <parameter name="sign">redacted</parameter>
        <parameter name="version">1.0.2</parameter>
        <parameter name="mode">lightbox</parameter>
        <parameter name="expy">19</parameter>
        <parameter name="returnCustomerCountry">CHE</parameter>
        <parameter name="theme">DT2015</parameter>
        <parameter name="acqErrorCode">50</parameter>
        <parameter name="uppReturnTarget">_top</parameter>
        <parameter name="expm">12</parameter>
      </userParameters>
    </transaction>
  </body>
</uppTransactionService>
"""
        expected = Payment(
            success=False,
            transaction_id='170720154219033737',
            merchant_id='1111111111',
            request_type='CAA',
            expiry_month=12,
            expiry_year=19,
            client_ref='1234',
            amount=Money(1.0, 'CHF'),
            payment_method='VIS',
            credit_card_country='CHE',

            error_code='1403',
            error_message='declined',
            error_detail='Declined',
            acquirer_error_code='50',
        )
        parsed = parse_notification_xml(xml)
        assertModelEqual(expected, parsed)

    def test_payment_in_unsupported_currency(self):
        xml = """<uppTransactionService version="1">
  <body merchantId="1111111111" testOnly="yes">
    <transaction refno="5" status="error">
      <uppTransactionId>170802095839802669</uppTransactionId>
      <amount>500</amount>
      <currency>RUB</currency>
      <error>
        <errorCode>-999</errorCode>
        <errorMessage>without error message</errorMessage>
        <errorDetail>not available payment method</errorDetail>
      </error>
      <userParameters>
        <parameter name="sign">redacted</parameter>
        <parameter name="version">1.0.2</parameter>
        <parameter name="mode">lightbox</parameter>
        <parameter name="theme">DT2015</parameter>
        <parameter name="uppReturnTarget">_top</parameter>
      </userParameters>
    </transaction>
  </body>
</uppTransactionService>"""
        expected = Payment(
            success=False,
            transaction_id='170802095839802669',
            merchant_id='1111111111',
            client_ref='5',
            amount=Money(5, 'RUB'),
            error_code='-999',
            error_message='without error message',
            error_detail='not available payment method',
        )
        parsed = parse_notification_xml(xml)
        assertModelEqual(expected, parsed)

    def test_pointspay(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<uppTransactionService version="1">
  <body merchantId="1111111111" testOnly="yes">
    <transaction refno="1234" status="success">
      <uppTransactionId>170928152808316732</uppTransactionId>
      <amount>300</amount>
      <currency>CHF</currency>
      <pmethod>PPA</pmethod>
      <reqtype>CAA</reqtype>
      <success>
        <authorizationCode>924837574</authorizationCode>
        <acqAuthorizationCode>949a42070f1a497fabbf6b0ddf20b0e4</acqAuthorizationCode>
        <responseMessage>PPA transaction Ok</responseMessage>
        <responseCode>01</responseCode>
      </success>
      <userParameters>
        <parameter name="sign">redacted</parameter>
        <parameter name="responseCode">01</parameter>
        <parameter name="mode">lightbox</parameter>
        <parameter name="sign2">68b727cce2575d6a1c1fdd34cc12cbe8204f78ea58ca3a2bea4725b0d907148c</parameter>
        <parameter name="theme">DT2015</parameter>
        <parameter name="uppReturnTarget">_top</parameter>
        <parameter name="version">1.0.2</parameter>
      </userParameters>
    </transaction>
  </body>
</uppTransactionService>"""
        expected = Payment(
            success=True,
            transaction_id='170928152808316732',
            merchant_id='1111111111',
            request_type='CAA',
            client_ref='1234',
            amount=Money(3, 'CHF'),
            payment_method='PPA',
            authorization_code='924837574',
            acquirer_authorization_code='949a42070f1a497fabbf6b0ddf20b0e4',
            response_code='01',
            response_message='PPA transaction Ok',
        )
        parsed = parse_notification_xml(xml)
        assertModelEqual(expected, parsed)
