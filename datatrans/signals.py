from django.dispatch import Signal

payment_done = Signal(providing_args=['instance', 'is_success', 'client_ref'])
alias_registration_done = Signal(providing_args=['instance', 'is_success', 'client_ref'])
charge_done = Signal(providing_args=['instance', 'is_success', 'client_ref'])
