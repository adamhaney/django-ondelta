django-ondelta
==============

A django model mixin that makes it easy to react to field value
changes on models. Supports an API similar to the model clean method.


Quick Start
-----------

Given that I have the model

    class MyModel(models.Model):
        mai_field = models.CharField()
        other_field = models.BooleanField()

And I want to be notified when mai_field's value is changed and
persisted I would simply need to modify my model to include a
`ondelta_mai_field` method.

    from ondelta.models import OnDeltaMixin

    class MyModel(OnDeltaMixin):
        mai_field = models.CharField()
        other_field = models.BooleanField()

        def ondelta_mai_field(self, old_value, new_value):
            print("mai field had the value of {}".format(old_value))
            print("but after we called save it had the value of {}".format(new_value))

This is the easiest method to watch a single field for changes, but
what if we want to perform an action that has an aggregate view
of all of the fields that were changed? `OnDeltaMixin` provides an
`ondelta_all` method for these cases; it is only called once for
each save.

    from ondelta.models import OnDeltaMixin

    class MyModel(OnDeltaMixin):
        mai_field = models.CharField()
        other_field = models.BooleanField()

        ondelta_all(self, fields_changed):
            if 'mai_field' in fields_changed and 'other_field' in fields_changed:
                print("Both fields changed during this save!")


Unsupported Field Types
-----------------------

Some field types are not supported: `ManyToManyField`, reverse `ManyToManyField`,
reverse `ForeignKey`, and reverse `OneToOneField` relations.  If you create an
`ondelta_field_name` method for one of these fields, it will **not** be called when
that field is changed.


Help
----

I like to help people as much as possible who are using my libraries,
the easiest way to get my attention is to tweet @adamhaney or open an
issue. As long as I'm able I'll help with any issues you have.
