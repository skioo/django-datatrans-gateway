from django.urls import include, path

from datatrans.views import example

urlpatterns = [
    path(r'^datatrans/', include('datatrans.urls')),
    path(r'^example/register-credit-card$', example.register_credit_card, name='example_register_credit_card'),
    path(r'^example/pay$', example.pay, name='example_pay'),
]
