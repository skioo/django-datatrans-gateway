"""
Example views for interactive testing of registering aliases and paying with datatrans.

You should restrict access if you chose to add them to your urlconf
(for instance with the 'staff_member_required' decorator).
"""

from django.forms import CharField, TextInput, forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from djmoney.forms import MoneyField
from moneyed import Money

from ..config import datatrans_js_url
from ..gateway import build_payment_parameters

CLIENT_REF_FIELD_SIZE = 18


class RegisterAliasForm(forms.Form):
    client_ref = CharField(
        required=True,
        max_length=CLIENT_REF_FIELD_SIZE,
        widget=TextInput(attrs={'size': CLIENT_REF_FIELD_SIZE})
    )


def register_alias(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = RegisterAliasForm(request.POST)
        if form.is_valid():
            payment_parameters = build_payment_parameters(
                value=Money(0, 'CHF'),
                client_ref=form.cleaned_data['client_ref']
            )
            context = {
                'title': 'Register credit card alias',
                'datatrans_js_url': datatrans_js_url,
                'use_alias': True,
            }
            context.update(payment_parameters._asdict())

            return render(request, 'datatrans/example/display-datatrans-form.html', context)
    else:
        form = RegisterAliasForm()

    return render(request, 'datatrans/example/display-form.html', {
        'title': 'Register credit card alias',
        'form': form
    })


class PayForm(forms.Form):
    value = MoneyField(min_value=0, default_currency='CHF')
    client_ref = CharField(
        required=True,
        max_length=CLIENT_REF_FIELD_SIZE,
        widget=TextInput(attrs={'size': CLIENT_REF_FIELD_SIZE})
    )


def pay(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = PayForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data['value']
            payment_parameters = build_payment_parameters(
                value=value,
                client_ref=form.cleaned_data['client_ref']
            )
            context = {
                'datatrans_js_url': datatrans_js_url,
                'title': 'Pay {}'.format(value),
            }
            context.update(payment_parameters._asdict())

            return render(request, 'datatrans/example/display-datatrans-form.html', context)
    else:
        form = PayForm()

    return render(request, 'datatrans/example/display-form.html', {
        'title': 'Payment',
        'form': form
    })
