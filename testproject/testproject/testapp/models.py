# -*- coding: utf-8 -*-

from ondelta.models import OnDeltaMixin

from django.db import models


class Foo(OnDeltaMixin):

    char_field = models.CharField(max_length=150)
    char_field_delta_count = models.IntegerField(default=0)

    def ondelta_char_field(self, old_value, new_value):
        self.char_field_delta_count += 1


class Bar(OnDeltaMixin):

    one_to_one = models.OneToOneField(Foo, related_name='one_to_one_reverse', null=True)
    foreign_key = models.ForeignKey(Foo, related_name='foreign_key_reverse', null=True)
    many_to_many = models.ManyToManyField(Foo, related_name='many_to_many_reverse')

    def ondelta_one_to_one(self, old, new):
        pass

    def ondelta_foreign_key(self, old, new):
        pass
