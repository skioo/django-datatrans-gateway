from django.test import TestCase
from moneyed import Money

from datatrans.gateway.refunding import build_refund_request_xml, parse_refund_response_xml
from datatrans.models import Refund
from .utils import assertModelEqual


class BuildRefundRequestTest(TestCase):
    def test_build_request(self):
        xml = build_refund_request_xml(
            value=Money(123, "CHF"),
            client_ref='abcdef',
            original_transaction_id='12345'
        )
        expected = """<?xml version='1.0' encoding='utf8'?>
<paymentService version="1"><body merchantId="1111111111"><transaction refno="abcdef"><request><amount>12300</amount><currency>CHF</currency><uppTransactionId>12345</uppTransactionId><transtype>06</transtype><sign>18a44815e3aedb09419e22b9dfcecccbdee99925f51e40fa519082badbf5e2dc</sign></request></transaction></body></paymentService>"""  # noqa
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
            is_success=True,
            transaction_id='171015120225118036',
            merchant_id='1111111111',
            request_type='COA',
            payment_transaction_id='170803184046388845',
            client_ref='nico-r',
            value=Money(1, 'CHF'),
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
            is_success=False,
            merchant_id='2222222222',
            request_type='COA',
            payment_transaction_id='170803184046388845',
            client_ref='nico-r',
            value=Money(1, 'CHF'),
            error_code='2000',
            error_message='access denied',
            error_detail='incorrect merchantId',
        )
        assertModelEqual(expected, parse_refund_response_xml(response))
