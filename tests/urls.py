from django.conf.urls import url, include

urlpatterns = [
    url(r'^datatrans/', include('datatrans.urls')),
    url(r'^examples/', include('datatrans.example_urls')),
]
