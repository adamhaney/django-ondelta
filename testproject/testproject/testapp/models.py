from ondelta.models import OnDeltaMixin

from django.db import models


class TestDeltaModel(OnDeltaMixin):

    char_field = models.CharField(max_length=150)
    int_field = models.IntegerField(default=0)

    def ondelta_char_field(self, old_value, new_value):
        self.int_field += 1
        self.save()
