from ondelta.models import OnDeltaMixin

from django.db import models


class TestDeltaModel(OnDeltaMixin):
    charfield = models.CharField(max_length=150)
    intfield = models.IntegerField(default=2)
