from django.conf.urls import include, url

from datatrans.views import example

urlpatterns = [
    url(r'^datatrans/', include('datatrans.urls')),
    url(r'^example/register-credit-card$', example.register_credit_card, name='example_register_credit_card'),
    url(r'^example/pay$', example.pay, name='example_pay'),
]
