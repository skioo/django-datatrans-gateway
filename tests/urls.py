from django.conf.urls import url, include

from datatrans.views import example

urlpatterns = [
    url(r'^datatrans/', include('datatrans.urls')),
    url(r'^example/register-alias$', example.register_alias, name='datatrans_example_register_alias'),
    url(r'^example/pay$', example.pay, name='datatrans_example_pay'),
]
