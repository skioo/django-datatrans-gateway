from django.test import TestCase
from moneyed import Money

from datatrans.gateway.refunding import build_refund_request_xml, parse_refund_response_xml
from datatrans.models import Refund
from .assertions import assertModelEqual


class BuildRefundRequestTest(TestCase):
    def test_build_request(self):
        xml = build_refund_request_xml(
            amount=Money(123, "CHF"),
            client_ref='abcdef',
            original_transaction_id='12345',
            merchant_id='1234567'
        )
        expected = """<?xml version='1.0' encoding='utf8'?>
<paymentService version="1"><body merchantId="1234567"><transaction refno="abcdef"><request><amount>12300</amount><currency>CHF</currency><uppTransactionId>12345</uppTransactionId><transtype>06</transtype><sign>cae361426f625bbe03a9ef0ef3c4daf27a7e16547191ec7b704cb1337d43fe22</sign></request></transaction></body></paymentService>"""  # noqa
        assert xml.decode() == expected


class ParseRefundResponseTest(TestCase):
    def test_success(self):
        response = """<?xml version='1.0' encoding='utf8'?>
<paymentService version='1'>
  <body merchantId='1111111111' status='accepted'>
    <transaction refno='nico-r' trxStatus='response'>
      <request>
        <amount>100</amount>
        <currency>CHF</currency>
        <uppTransactionId>170803184046388845</uppTransactionId>
        <transtype>06</transtype>
        <sign>d6e112b7a16269893f0c32147618475f03a32fb03ebcfcba066932433f15da57</sign>
        <reqtype>COA</reqtype>
      </request>
      <response>
        <responseCode>01</responseCode>
        <responseMessage>credit succeeded</responseMessage>
        <uppTransactionId>171015120225118036</uppTransactionId>
        <authorizationCode>225128037</authorizationCode>
        <acqAuthorizationCode>120225</acqAuthorizationCode>
      </response>
    </transaction>
  </body>
</paymentService>"""
        expected = Refund(
            success=True,
            transaction_id='171015120225118036',
            merchant_id='1111111111',
            request_type='COA',
            payment_transaction_id='170803184046388845',
            client_ref='nico-r',
            amount=Money(1, 'CHF'),
            response_code='01',
            response_message='credit succeeded',
            authorization_code='225128037',
            acquirer_authorization_code='120225',
        )
        assertModelEqual(expected, parse_refund_response_xml(response))

    def test_incorrect_merchant_id(self):
        response = """<?xml version='1.0' encoding='utf8'?>
<paymentService version='1'>
  <body merchantId='2222222222' status='accepted'>
    <transaction refno='nico-r' trxStatus='error'>
      <request>
        <amount>100</amount>
        <currency>CHF</currency>
        <uppTransactionId>170803184046388845</uppTransactionId>
        <transtype>06</transtype>
        <sign>b220f990f60b28eadb811c46c77a6501e6fe7063134c6741544c60ca7c5a610a</sign>
        <reqtype>COA</reqtype>
      </request>
      <error>
        <errorCode>2000</errorCode>
        <errorMessage>access denied</errorMessage>
        <errorDetail>incorrect merchantId</errorDetail>
      </error>
    </transaction>
  </body>
</paymentService>"""
        expected = Refund(
            success=False,
            merchant_id='2222222222',
            request_type='COA',
            payment_transaction_id='170803184046388845',
            client_ref='nico-r',
            amount=Money(1, 'CHF'),
            error_code='2000',
            error_message='access denied',
            error_detail='incorrect merchantId',
        )
        assertModelEqual(expected, parse_refund_response_xml(response))

    def test_invalid_payment_transaction_id(self):
        response = """<?xml version='1.0' encoding='utf8'?>
<paymentService version='1'>
  <body merchantId='2222222222' status='error'>
    <transaction refno='theclientref-r' trxStatus='error'>
      <request>
        <amount>100</amount>
        <currency>CHF</currency>
        <uppTransactionId>thetransactionid</uppTransactionId>
        <transtype>06</transtype>
        <sign>15deeff44956dd3ffcf39cbcdc45e593f4dcfc0a0bf0c02aafb40c608050041f</sign>
      </request>
      <error>
        <errorCode>2022</errorCode>
        <errorMessage>invalid value</errorMessage>
        <errorDetail> authorizationCode,</errorDetail>
      </error>
    </transaction>
  </body>
</paymentService>"""
        expected = Refund(
            success=False,
            merchant_id='2222222222',
            payment_transaction_id='thetransactionid',
            client_ref='theclientref-r',
            amount=Money(1, 'CHF'),
            error_code='2022',
            error_message='invalid value',
            error_detail=' authorizationCode,',
        )
        assertModelEqual(expected, parse_refund_response_xml(response))
