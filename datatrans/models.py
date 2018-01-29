import calendar
import uuid

from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from djmoney.models.fields import MoneyField

from .signals import alias_registration_done, payment_by_user_done, payment_with_alias_done, refund_done

CLIENT_REF_FIELD_SIZE = 18

expiry_month_validators = [MinValueValidator(1), MaxValueValidator(12)]
expiry_year_validators = [MinValueValidator(0), MaxValueValidator(99)]


def compute_expiry_date(two_digit_year: int, month: int) -> date:
    year = 2000 + two_digit_year
    _, last_day_of_month = calendar.monthrange(year, month)
    return date(year=year, month=month, day=last_day_of_month)


class TransactionBase(models.Model):
    """"
    All the fields that are common to the different transaction types.
    Some of the fields declared here are redefined in subclasses:
    For instance expiry_month and expiry_year are optional in this base class,
    but in an alias registration those fields are mandatory.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    merchant_id = models.CharField(db_index=True, max_length=255)
    transaction_id = models.CharField(unique=True, max_length=18, blank=True, null=True)
    client_ref = models.CharField(db_index=True, max_length=18)
    amount = MoneyField(max_digits=12, decimal_places=2, default_currency='CHF')
    request_type = models.CharField(max_length=3, blank=True)

    expiry_month = models.IntegerField(null=True, blank=True, validators=expiry_month_validators)
    expiry_year = models.IntegerField(null=True, blank=True, validators=expiry_year_validators)

    expiry_date = models.DateField(null=True, blank=True)  # A field in the database so we can search for expired cards
    credit_card_country = models.CharField(db_index=True, max_length=3, blank=True)

    success = models.BooleanField()

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
        if self.expiry_year is not None and self.expiry_month is not None:
            self.expiry_date = compute_expiry_date(two_digit_year=self.expiry_year, month=self.expiry_month)
        super().save(*args, **kwargs)

    def _send_signal(self, signal):
        signal.send(sender=None, instance=self, success=self.success)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} {} ({})'.format(
            self.__class__.__name__,
            self.transaction_id,
            'successful' if self.success else 'failed'
        )

    def __repr__(self):
        c = self.__class__
        return '<{}.{} object at {}: {}>'.format(c.__module__, c.__name__, hex(id(self)), vars(self))


class AliasRegistration(TransactionBase):
    card_alias = models.CharField(db_index=True, max_length=20, blank=True)
    masked_card_number = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(db_index=True, max_length=3)
    expiry_month = models.IntegerField(validators=expiry_month_validators)
    expiry_year = models.IntegerField(validators=expiry_year_validators)

    def send_signal(self):
        self._send_signal(alias_registration_done)

    def __str__(self):
        return 'Alias: {} {}'.format(self.payment_method, self.masked_card_number)


class Payment(TransactionBase):
    transaction_id = models.CharField(unique=True, max_length=18)
    card_alias = models.CharField(db_index=True, max_length=20, blank=True)
    masked_card_number = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(db_index=True, max_length=3, blank=True)

    def send_signal(self):
        if self.card_alias:
            self._send_signal(payment_with_alias_done)
        else:
            self._send_signal(payment_by_user_done)


class Refund(TransactionBase):
    payment_transaction_id = models.CharField(db_index=True, max_length=18)

    def send_signal(self):
        self._send_signal(refund_done)
