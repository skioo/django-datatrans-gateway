from django.urls import path

from .views import webhook

urlpatterns = [
    path(r'webhook', webhook.webhook_handler, name='datatrans_webhook'),
]
