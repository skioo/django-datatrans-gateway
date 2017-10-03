django-datatrans-gateway
========================

[![Build Status](https://travis-ci.org/skioo/django-datatrans-gateway.svg?branch=master)](https://travis-ci.org/skioo/django-datatrans-gateway)
[![PyPI version](https://badge.fury.io/py/django-datatrans-gateway.svg)](https://badge.fury.io/py/django-datatrans-gateway)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A django integration for the datatrans payment gateway.

Supports:
- Direct payment by the user
- Registration of a credit card alias by the user, followed by one or more charges (without the user being present).


This implementation:
- Handles the exchanges with datatrans, including the signing of requests and the verification of the signature of notifications.
- Introduces persistent models for Payment, AliasRegistration, Charge. All exchanges with datatrans are stored in the database for debuggability and auditability.
- Due to the asynchronous nature of the datatrans interaction, sends signals whenever a notification (success or failure) is received from datatrans.


Requirements
------------

* Python: 3.4 and over
* Django: Tested with django 1.11


Usage
-----

Add datatrans to your `INSTALLED_APPS`:

    INSTALLED_APPS = (
    ...
    'datatrans.apps.DatatransConfig',
    )


Include `datatrans-urls` to the urlpatterns in your urls.py, for instance:

    urlpatterns = [
        url(r'^datatrans/', include('datatrans.urls')),
    ]

Configure the callback url in your upp

In your settings.py, enter the configuration for your web and mpo merchants. For instance:

    DATATRANS = {
        'WEB_MERCHANT_ID': '1111111111',
        'WEB_HMAC_KEY': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
        'MPO_MERCHANT_ID': '2222222222',
        'MPO_HMAC_KEY': 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    }


Troubleshooting
---------------

The first thing the code does when it receives a notification is logging a `datatrans-notification` event with structlog.

If you don't see a payment (or a payment error) in the database, and you are sure you've properly configured the callback in the upp,
then start by looking in the log for a `datatrans-notification`
