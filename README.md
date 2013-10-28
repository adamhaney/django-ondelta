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
            print "mai field had the value of", mai_field
            print "but by the time we called save it had the value of", new_value

This is the easiest method to watch a single field for changes but
what about if we want to perform an action that has an aggregate view
of all of the fields that were changed? OnDeltaMixin provides an
`ondelta_all` method for these cases which is only called once for
each save.

    from ondelta.models import OnDeltaMixin

    class MyModel(OnDeltaMixin):
        mai_field = models.CharField()
        other_field = models.BooleanField()

        ondelta_all(self, fields_changed):
            if fields_changed['other_field']['old'] == True:
                print "other field was true and is now", fields_changed['other_field']['new']
                print "We also have access to", fields_changed['mai_field']['old']



Design Considerations
---------------------

All effort to be made not to over notify on changes. Any comparison
problems should fail in a way that does NOT duplication
notifications. Field comparisons should also not cause other problems
in the model (for example causing a child to be unable to persist).


Help
----

I like to help people as much as possible who are using my libraries,
the easiest way to get my attention is to tweet @adamhaney or open an
issue. As long as I'm able I'll help with any issues you have.