"""
Example views for interactive testing paying and registering credit cards with datatrans.

You should restrict access (maybe with 'staff_member_required') if you chose to add these views to your urlconf.
"""

from django.forms import CharField, TextInput, forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from djmoney.forms import MoneyField

from ..config import datatrans_js_url
from ..gateway import build_payment_parameters, build_register_credit_card_parameters
from ..models import CLIENT_REF_FIELD_SIZE


class PayForm(forms.Form):
    amount = MoneyField(min_value=0, default_currency='CHF')
    client_ref = CharField(
        required=True,
        max_length=CLIENT_REF_FIELD_SIZE,
        widget=TextInput(attrs={'size': CLIENT_REF_FIELD_SIZE})
    )


def pay(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = PayForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            parameters = build_payment_parameters(
                amount=amount,
                client_ref=form.cleaned_data['client_ref']
            )
            context = {
                'title': 'Pay {}'.format(amount),
                'datatrans_js_url': datatrans_js_url,
            }
            context.update(parameters._asdict())

            return render(request, 'datatrans/example/datatrans_form.html', context)
    else:
        form = PayForm()

    return render(request, 'datatrans/example/form.html', {
        'title': 'Payment',
        'form': form
    })


###################################################################

class RegisterCreditCardForm(forms.Form):
    client_ref = CharField(
        required=True,
        max_length=CLIENT_REF_FIELD_SIZE,
        widget=TextInput(attrs={'size': CLIENT_REF_FIELD_SIZE})
    )


def register_credit_card(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = RegisterCreditCardForm(request.POST)
        if form.is_valid():
            parameters = build_register_credit_card_parameters(client_ref=form.cleaned_data['client_ref'])
            context = {
                'title': 'Register credit card',
                'datatrans_js_url': datatrans_js_url,
            }
            context.update(parameters._asdict())

            return render(request, 'datatrans/example/datatrans_form.html', context)
    else:
        form = RegisterCreditCardForm()

    return render(request, 'datatrans/example/form.html', {
        'title': 'Register credit card',
        'form': form
    })
