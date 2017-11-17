from django.conf.urls import url
from django.contrib import admin
from django.forms import CharField, TextInput, forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import format_html
from djmoney.forms import MoneyField
from moneyed.localization import format_money

from .gateway import pay_with_alias, refund
from .models import AliasRegistration, Payment, Refund


def expiry(obj):
    if obj.expiry_month is not None and obj.expiry_year is not None:
        return format_html('{}/{}', obj.expiry_month, obj.expiry_year)


def amount(obj):
    return format_money(obj.amount)


class PayWithAliasForm(forms.Form):
    amount = MoneyField(min_value=0, default_currency='CHF')
    client_ref = CharField(required=True, max_length=18, widget=TextInput(attrs={'size': 18}))


def pay_with_alias_form(request, alias_registration_id):
    if request.method == 'POST':
        form = PayWithAliasForm(request.POST)
        if form.is_valid():
            result = pay_with_alias(
                amount=form.cleaned_data['amount'],
                alias_registration_id=alias_registration_id,
                client_ref=form.cleaned_data['client_ref'],
            )
            # As confirmation we take the user to the detail page of the payment.
            return HttpResponseRedirect(reverse('admin:datatrans_payment_change', args=[result.id]))
    else:
        form = PayWithAliasForm()

    alias_registration = get_object_or_404(AliasRegistration, pk=alias_registration_id)

    return render(
        request,
        'admin/datatrans/form.html',
        {
            'title': 'Pay with alias of credit card {}'.format(alias_registration.masked_card_number),
            'form': form,
            'opts': AliasRegistration._meta,  # Used to setup the navigation / breadcrumbs of the page
        }
    )


@admin.register(AliasRegistration)
class AliasRegistrationAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    readonly_fields = ['created', 'modified', 'expiry_date', 'pay_with_alias_button']
    list_display = [
        'transaction_id', 'created', 'success', 'client_ref', amount, 'payment_method', 'card_alias',
        'masked_card_number', expiry,
        'credit_card_country', 'error_code', 'pay_with_alias_button']
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
                r'^(?P<alias_registration_id>[0-9a-f-]+)/pay_with_alias/$',
                self.admin_site.admin_view(pay_with_alias_form),
                name='datatrans_alias_pay',
            ),
        ]
        return my_urls + urls

    def pay_with_alias_button(self, obj):
        if obj.success:
            return format_html('<a class="button" href="{}">Pay with alias</a>',
                               reverse('admin:datatrans_alias_pay', args=[obj.pk]))
        else:
            return '-'

    pay_with_alias_button.short_description = 'Pay with alias'  # type: ignore


class RefundPaymentForm(forms.Form):
    amount = MoneyField(min_value=0, default_currency='CHF')


def refund_payment_form(request, payment_id):
    if request.method == 'POST':
        form = RefundPaymentForm(request.POST)
        if form.is_valid():
            result = refund(
                amount=form.cleaned_data['amount'],
                payment_id=payment_id)
            # As confirmation we take the user to the edit page of the refund.
            return HttpResponseRedirect(reverse('admin:datatrans_refund_change', args=[result.id]))
    else:
        form = RefundPaymentForm()

    payment = get_object_or_404(Payment, pk=payment_id)

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
    readonly_fields = ['created', 'modified']
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
                r'^(?P<payment_id>[0-9a-f-]+)/refund/$',
                self.admin_site.admin_view(refund_payment_form),
                name='datatrans_payment_refund',
            ),
        ]
        return my_urls + urls

    def refund_button(self, obj):
        if obj.success:
            return format_html('<a class="button" href="{}">Refund</a>',
                               reverse('admin:datatrans_payment_refund', args=[obj.pk]))
        else:
            return '-'

    refund_button.short_description = 'Refund'  # type: ignore


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    readonly_fields = ['created', 'modified']
    list_display = [
        'transaction_id', 'payment_transaction_id', 'created', 'success', 'client_ref', amount, 'error_code',
        'error_message']
    list_display_links = ['transaction_id', 'payment_transaction_id']

    search_fields = [
        'transaction_id', 'payment_transaction_id', 'created', 'client_ref', 'amount', 'response_code',
        'authorization_code', 'acquirer_authorization_code', 'error_code', 'error_message', 'error_detail']
    list_filter = ['success', ('amount_currency', admin.AllValuesFieldListFilter)]
    ordering = ['-created']
