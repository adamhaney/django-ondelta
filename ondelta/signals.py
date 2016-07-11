# -*- coding: utf-8 -*-
from django.dispatch import Signal

post_ondelta_signal = Signal(providing_args=['fields_changed', 'instance'])
