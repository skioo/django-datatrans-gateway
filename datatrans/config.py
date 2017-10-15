from django.conf import settings
import hashlib
import hmac
import os
from typing import Any, Sequence

web_merchant_id = settings.DATATRANS['WEB_MERCHANT_ID']
_web_hmac_key = bytearray.fromhex(settings.DATATRANS['WEB_HMAC_KEY'])
mpo_merchant_id = settings.DATATRANS['MPO_MERCHANT_ID']
_mpo_hmac_key = bytearray.fromhex(settings.DATATRANS['MPO_HMAC_KEY'])

if settings.DATATRANS.get('ENVIRONMENT') == 'PRODUCTION':
    _base_url = 'https://payment.datatrans.biz/'
else:
    _base_url = 'https://pilot.datatrans.biz/'

datatrans_js_url = os.path.join(_base_url, 'upp/payment/js/datatrans-1.0.2.js')
datatrans_authorize_url = os.path.join(_base_url, 'upp/jsp/XML_authorize.jsp')
datatrans_processor_url = os.path.join(_base_url, 'upp/jsp/XML_processor.jsp')


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
