django-ondelta
==============

A django model mixin that makes it easy to react to field value
changes on models. Supports an API similar to the model clean method.


Design Considerations
---------------------

All effort to be made not to over notify on changes. Any comparison
problems should fail in a way that does NOT duplication
notifications. Field comparisons should also not cause other problems
in the model (for example causing a child to be unable to persist).