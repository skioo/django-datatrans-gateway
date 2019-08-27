import hashlib
import hmac
import os
from typing import Any, Sequence

from django.conf import settings

web_merchant_id = settings.DATATRANS['WEB_MERCHANT_ID']
_web_hmac_key = bytearray.fromhex(settings.DATATRANS['WEB_HMAC_KEY'])
mpo_merchant_id = settings.DATATRANS['MPO_MERCHANT_ID']
_mpo_hmac_key = bytearray.fromhex(settings.DATATRANS['MPO_HMAC_KEY'])

if settings.DATATRANS.get('ENVIRONMENT') == 'PRODUCTION':
    _pay_base_url = 'https://pay.datatrans.com/'
    _api_base_url = 'https://api.datatrans.com/'
else:
    _pay_base_url = 'https://pay.sandbox.datatrans.com/'
    _api_base_url = 'https://api.sandbox.datatrans.com/'

datatrans_js_url = os.path.join(_pay_base_url, 'upp/payment/js/datatrans-2.0.0.min.js')
datatrans_authorize_url = os.path.join(_api_base_url, 'upp/jsp/XML_authorize.jsp')
datatrans_processor_url = os.path.join(_api_base_url, 'upp/jsp/XML_processor.jsp')


def sign_web(*values: Any) -> str:
    return _sign(values, _web_hmac_key)


def sign_mpo(*values: Any) -> str:
    return _sign(values, _mpo_hmac_key)


def _sign(values: Sequence[Any], key: bytearray) -> str:
    s = ''.join(map(str, values))
    return hmac.new(
        key=key,
        msg=s.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
