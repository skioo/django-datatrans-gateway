from django.conf.urls import url

from .views import notify

urlpatterns = [
    url(r'notify$', notify.notify_handler, name='datatrans_notify'),
]
