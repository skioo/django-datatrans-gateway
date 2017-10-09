from django.conf.urls import url
from django.contrib import admin
from django.forms import CharField, TextInput, forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import format_html
from djmoney.forms import MoneyField
from moneyed.localization import format_money

from .gateway import charge
from .models import AliasRegistration, Charge, Payment


def expiry(obj):
    if obj.expiry_month is not None and obj.expiry_year is not None:
        return format_html('{}/{}', obj.expiry_month, obj.expiry_year)


def value(obj):
    return format_money(obj.value)


class ChargeForm(forms.Form):
    value = MoneyField(min_value=0, default_currency='CHF')
    client_ref = CharField(required=True, max_length=18, widget=TextInput(attrs={'size': 18}))


def charge_form(request, alias_registration_id):
    if request.method == 'POST':
        form = ChargeForm(request.POST)
        if form.is_valid():
            result = charge(
                value=form.cleaned_data['value'],
                client_ref=form.cleaned_data['client_ref'],
                alias_registration_id=alias_registration_id,
            )
            # A bit lazy, we just take the user to the edit page of the charge or error.
            charge_url = reverse('admin:datatrans_charge_change', args=(result.id,))
            return HttpResponseRedirect(charge_url)
    else:
        form = ChargeForm()

    alias_registration = get_object_or_404(AliasRegistration, pk=alias_registration_id)

    return render(
        request,
        'admin/datatrans/charge.html',
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
        'transaction_id', 'created', 'is_success', 'client_ref', 'payment_method', 'masked_card_number', expiry,
        'credit_card_country', 'error_code', 'charge_button']
    search_fields = [
        'transaction_id', 'created', 'expiry_date', 'payment_method', 'masked_card_number', 'expiry_month',
        'expiry_year', 'card_alias', 'credit_card_country', 'client_ref', 'error_code', 'error_message',
        'error_detail']
    list_filter = ['is_success', 'payment_method', 'credit_card_country']
    ordering = ['-created']

    def get_urls(self):
        urls = super(AliasRegistrationAdmin, self).get_urls()
        my_urls = [
            url(
                r'^(?P<alias_registration_id>[0-9a-f-]+)/charge/$',
                self.admin_site.admin_view(charge_form),
                name='charge',
            ),
        ]
        return my_urls + urls

    def charge_button(self, obj):
        if obj.is_success:
            return format_html(
                '<a class="button" href="{}">Charge</a>',
                reverse('admin:charge', args=[obj.pk]),
            )


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    readonly_fields = ['created']
    list_display = [
        'transaction_id', 'created', 'is_success', 'client_ref', value, 'masked_card_number', expiry,
        'credit_card_country',
        'card_alias', 'error_code', 'error_message']
    search_fields = [
        'transaction_id', 'created', 'value', 'masked_card_number', 'expiry_month', 'expiry_year', 'card_alias',
        'credit_card_country', 'client_ref', 'error_code', 'error_message']
    list_filter = ['is_success', 'credit_card_country', ('value_currency', admin.AllValuesFieldListFilter)]
    ordering = ['-created']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    readonly_fields = ['created']
    list_display = [
        'transaction_id', 'created', 'is_success', 'client_ref', value, 'payment_method', 'masked_card_number', expiry,
        'credit_card_country', 'error_code', 'error_message']
    search_fields = [
        'transaction_id', 'created', 'payment_method', 'masked_card_number', 'value', 'expiry_month',
        'expiry_year', 'credit_card_country', 'client_ref', 'error_code', 'error_message',
        'acquirer_error_code']
    list_filter = ['is_success', 'payment_method', 'credit_card_country',
                   ('value_currency', admin.AllValuesFieldListFilter)]
    ordering = ['-created']
