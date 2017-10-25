from django.dispatch import Signal

alias_registration_done = Signal(providing_args=['instance', 'success'])
payment_done = Signal(providing_args=['instance', 'success'])
refund_done = Signal(providing_args=['instance', 'success'])
