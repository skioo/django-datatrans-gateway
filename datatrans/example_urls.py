from django.conf.urls import url

from .views import example

urlpatterns = [
    url(r'register-alias$', example.register_alias),
    url(r'payment$', example.pay),
]
