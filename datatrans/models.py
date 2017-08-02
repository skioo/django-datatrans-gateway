import calendar
from datetime import date

from django.db import models
from djmoney.models.fields import MoneyField


def compute_expiry_date(two_digit_year: int, month: int) -> date:
    year = 2000 + two_digit_year
    _, last_day_of_month = calendar.monthrange(year, month)
    return date(year=year, month=month, day=last_day_of_month)


class DatatransBase(models.Model):
    transaction_id = models.CharField(unique=True, max_length=18)
    created = models.DateTimeField(auto_now_add=True)
    is_success = models.BooleanField()
    client_ref = models.CharField(db_index=True, max_length=18)
    merchant_id = models.CharField(db_index=True, max_length=255)
    request_type = models.CharField(max_length=3)
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    expiry_date = models.DateField()
    value = MoneyField(max_digits=10, decimal_places=2, default_currency='CHF')
    credit_card_country = models.CharField(max_length=3)

    # If it's a success
    response_code = models.CharField(max_length=4, blank=True)
    response_message = models.CharField(max_length=255, blank=True)
    authorization_code = models.CharField(max_length=255, blank=True)
    acquirer_authorization_code = models.CharField(max_length=255, blank=True)

    # If it's an error
    error_code = models.CharField(max_length=7, blank=True)
    error_message = models.CharField(max_length=255, blank=True)
    error_detail = models.CharField(max_length=255, blank=True)
    acquirer_error_code = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        self.expiry_date = compute_expiry_date(two_digit_year=self.expiry_year, month=self.expiry_month)
        super(DatatransBase, self).save(*args, **kwargs)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} {} ({})'.format(
            self.__class__.__name__,
            self.transaction_id,
            'successful' if self.is_success else 'failed'
        )

    def __repr__(self):
        c = self.__class__
        return '<{}.{} object at {}: {}>'.format(c.__module__, c.__name__, hex(id(self)), vars(self))


class Payment(DatatransBase):
    masked_card_number = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(max_length=3)


class AliasRegistration(DatatransBase):
    masked_card_number = models.CharField(max_length=255)
    card_alias = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=3)


class Charge(DatatransBase):
    masked_card_number = models.CharField(max_length=255, blank=True)
    card_alias = models.CharField(max_length=20)
