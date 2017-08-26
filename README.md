[![Build Status](https://travis-ci.org/skioo/django-datatrans-gateway.svg?branch=master)](https://travis-ci.org/skioo/django-datatrans-gateway)


An integration for the datatrans payment gateway.

Supports:
- Direct payment by the user
- Registration of a credit card alias by the user, followed by one or more charges (without the user being present).


This implementation:
- Handles the exchanges with datatrans, including the signing of requests and the verification of the signature of notifications.
- Introduces persistent models for Payment, AliasRegistration, Charge. All exchanges with datatrans are stored in the database for debuggability and auditability.
- Due to the asynchronous nature of the datatrans interaction, sends signals whenever a notification (success or failure) is received from datatrans.

----

To work on this code:

    pip install -e .

To run tests:

    tox

To release a version to pypi:
- Edit \_\_version\_\_ in \_\_init\_\_.py
- Push and wait for the build to succeed
- Create a release in github, travis will build and deploy the new version to pypi: https://pypi.python.org/pypi/django-datatrans-gateway

