from django.conf.urls import url

from .views import webhook

urlpatterns = [
    url(r'webhook$', webhook.webhook_handler, name='datatrans_webhook'),
]
