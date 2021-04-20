from django.dispatch import Signal

alias_registration_done = Signal()
payment_by_user_done = Signal()
payment_with_alias_done = Signal()
refund_done = Signal()
