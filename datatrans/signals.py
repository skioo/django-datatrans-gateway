from django.dispatch import Signal

alias_registration_done = Signal(providing_args=['instance', 'is_success'])
payment_done = Signal(providing_args=['instance', 'is_success'])
refund_done = Signal(providing_args=['instance', 'is_success'])
