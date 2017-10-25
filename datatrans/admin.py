from django.conf.urls import url
from django.contrib import admin
from django.forms import CharField, TextInput, forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import format_html
from djmoney.forms import MoneyField
from moneyed.localization import format_money

from .gateway import charge, refund
from .models import AliasRegistration, Payment, Refund


def expiry(obj):
    if obj.expiry_month is not None and obj.expiry_year is not None:
        return format_html('{}/{}', obj.expiry_month, obj.expiry_year)


def amount(obj):
    return format_money(obj.amount)


class ChargeForm(forms.Form):
    amount = MoneyField(min_value=0, default_currency='CHF')
    client_ref = CharField(required=True, max_length=18, widget=TextInput(attrs={'size': 18}))


def charge_form(request, alias_registration_id):
    if request.method == 'POST':
        form = ChargeForm(request.POST)
        if form.is_valid():
            result = charge(
                amount=form.cleaned_data['amount'],
                alias_registration_id=alias_registration_id,
                client_ref=form.cleaned_data['client_ref'],
            )
            # As confirmation we just take the user to the edit page of the payment.
            payment_detail_url = reverse('admin:datatrans_payment_change', args=(result.id,))
            return HttpResponseRedirect(payment_detail_url)
    else:
        form = ChargeForm()

    alias_registration = get_object_or_404(AliasRegistration, pk=alias_registration_id)

    return render(
        request,
        'admin/datatrans/form.html',
        {
            'title': 'Charge credit card with number {}'.format(alias_registration.masked_card_number),
            'form': form,
            'opts': AliasRegistration._meta,  # Used to setup the navigation / breadcrumbs of the page
        }
    )


@admin.register(AliasRegistration)
class AliasRegistrationAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    readonly_fields = ['created', 'expiry_date', 'charge_button']
    list_display = [
        'transaction_id', 'created', 'success', 'client_ref', amount, 'payment_method', 'card_alias',
        'masked_card_number', expiry,
        'credit_card_country', 'error_code', 'charge_button']
    search_fields = [
        'transaction_id', 'created', 'expiry_date', 'payment_method', 'card_alias', 'masked_card_number',
        'expiry_month', 'expiry_year', 'credit_card_country', 'client_ref', 'response_code',
        'authorization_code', 'acquirer_authorization_code', 'error_code', 'error_message', 'error_detail']
    list_filter = ['success', 'payment_method', 'credit_card_country']
    ordering = ['-created']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(
                r'^(?P<alias_registration_id>[0-9a-f-]+)/charge/$',
                self.admin_site.admin_view(charge_form),
                name='charge',
            ),
        ]
        return my_urls + urls

    def charge_button(self, obj):
        if obj.success:
            return format_html(
                '<a class="button" href="{}">Charge</a>',
                reverse('admin:charge', args=[obj.pk]),
            )

    charge_button.short_description = 'Charge'  # type: ignore


class RefundForm(forms.Form):
    amount = MoneyField(min_value=0, default_currency='CHF')


def refund_form(request, transaction_id):
    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            result = refund(
                amount=form.cleaned_data['amount'],
                transaction_id=transaction_id)
            # As confirmation we just take the user to the edit page of the refund.
            refund_detail_url = reverse('admin:datatrans_refund_change', args=(result.id,))
            return HttpResponseRedirect(refund_detail_url)
    else:
        form = RefundForm()

    payment = get_object_or_404(Payment, transaction_id=transaction_id)

    return render(
        request,
        'admin/datatrans/form.html',
        {
            'title': 'Refund for original payment of {}, with {}'.format(payment.amount, payment.masked_card_number),
            'form': form,
            'opts': Payment._meta,  # Used to setup the navigation / breadcrumbs of the page
        }
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    readonly_fields = ['created']
    list_display = [
        'transaction_id', 'created', 'success', 'client_ref', amount, 'payment_method', 'card_alias',
        'masked_card_number', expiry,
        'credit_card_country', 'error_code', 'refund_button']
    search_fields = [
        'transaction_id', 'created', 'expiry_date', 'payment_method', 'card_alias', 'masked_card_number', 'amount',
        'expiry_month', 'expiry_year', 'credit_card_country', 'client_ref', 'response_code',
        'authorization_code', 'acquirer_authorization_code', 'error_code', 'error_message', 'error_detail']
    list_filter = ['success', 'payment_method', 'credit_card_country',
                   ('amount_currency', admin.AllValuesFieldListFilter)]
    ordering = ['-created']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(
                r'^(?P<transaction_id>\w+)/refund/$',
                self.admin_site.admin_view(refund_form),
                name='refund',
            ),
        ]
        return my_urls + urls

    def refund_button(self, obj):
        if obj.success:
            return format_html(
                '<a class="button" href="{}">Refund</a>',
                reverse('admin:refund', args=[obj.transaction_id]),
            )

    refund_button.short_description = 'Refund'  # type: ignore


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    readonly_fields = ['created']
    list_display = [
        'transaction_id', 'payment_transaction_id', 'created', 'success', 'client_ref', amount, 'error_code',
        'error_message']
    list_display_links = ['transaction_id', 'payment_transaction_id']

    search_fields = [
        'transaction_id', 'payment_transaction_id', 'created', 'client_ref', 'amount', 'response_code',
        'authorization_code', 'acquirer_authorization_code', 'error_code', 'error_message', 'error_detail']
    list_filter = ['success', ('amount_currency', admin.AllValuesFieldListFilter)]
    ordering = ['-created']
