from django.dispatch import Signal

alias_registration_done = Signal(providing_args=['instance', 'is_success', 'client_ref'])
payment_done = Signal(providing_args=['instance', 'is_success', 'client_ref'])
refund_done = Signal(providing_args=['instance', 'is_success', 'client_ref'])
