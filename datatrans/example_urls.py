from django.conf.urls import url

from .views import example

urlpatterns = [
    url(r'register-alias$', example.register_alias, name='datatrans_example_register_alias'),
    url(r'pay$', example.pay, name='datatrans_example_pay'),
]
