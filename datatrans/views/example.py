from django.forms import CharField, TextInput, forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from djmoney.forms import MoneyField
from moneyed import Money

from ..config import datatrans_js_url
from ..gateway import build_payment_parameters


class RegisterAliasForm(forms.Form):
    client_ref = CharField(required=True, max_length=18, widget=TextInput(attrs={'size': 18}))


def register_alias(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = RegisterAliasForm(request.POST)
        if form.is_valid():
            payment_parameters = build_payment_parameters(
                value=Money(0, 'CHF'),
                client_ref=form.cleaned_data['client_ref']
            )
            context = {
                **payment_parameters._asdict(),
                'title': 'Register credit card alias',
                'datatrans_js_url': datatrans_js_url,
                'use_alias': True,
            }

            return render(request, 'datatrans/example/display-datatrans-form.html', context)
    else:
        form = RegisterAliasForm()

    return render(request, 'datatrans/example/display-form.html', {
        'title': 'Register credit card alias',
        'form': form
    })


class PayForm(forms.Form):
    value = MoneyField(min_value=0, default_currency='CHF')
    client_ref = CharField(required=True, max_length=18, widget=TextInput(attrs={'size': 18}))


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
                **payment_parameters._asdict(),
                'datatrans_js_url': datatrans_js_url,
                'title': 'Pay {}'.format(value),
            }
            return render(request, 'datatrans/example/display-datatrans-form.html', context)
    else:
        form = PayForm()

    return render(request, 'datatrans/example/display-form.html', {
        'title': 'Payment',
        'form': form
    })
