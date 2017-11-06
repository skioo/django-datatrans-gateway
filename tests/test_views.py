from django.test import Client, TestCase
from django.urls import reverse


class WebhookViewTest(TestCase):
    def test_it_should_process_a_webhook(self):
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
        response = Client().post(reverse('datatrans_webhook'),
                                 content_type='text/xml', data=xml)

        assert response.status_code == 200


class ExampleViewsTest(TestCase):
    def test_it_should_show_a_form_for_the_example_register_credit_card_page(self):
        response = Client().get(reverse('example_register_credit_card'))
        assert response.status_code == 200

    def test_it_should_show_a_form_for_the_example_pay_page(self):
        response = Client().get(reverse('example_pay'))
        assert response.status_code == 200
