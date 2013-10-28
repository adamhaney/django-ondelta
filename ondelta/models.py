import copy
import logging

from django.db import models

logger = logging.getLogger(__name__)


class OnDeltaMixin(models.Model):

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super_return = super(OnDeltaMixin, self).__init__(*args, **kwargs)
        self._ondelta_snapshot_state()
        return super_return

    def _ondelta_snapshot_state(self):
        self.model_snapshot = copy.deepcopy(self)

    def _ondelta_fields_to_watch(self):
        """
        This gives us all the fields that we should care about changes
        for, excludes fields added by tests (nose adds 'c') and the id
        which is an implementation detail of django
        """
        return set(self.model_snapshot._meta.get_all_field_names()) - set(['c', 'id'])

    def _ondelta_get_differences(self):
        fields_changed = {}
        for field in self._ondelta_fields_to_watch():
            try:
                snapshot_value = getattr(self.model_snapshot, field)
            except:
                logger.exception("Failed to retrieve the old value of {}.{} for comparison".format(__name__, field))
                continue

            try:
                current_value = getattr(self, field)
            except:
                logger.exception("Failed to retrieve the new value of {}.{} for comparison".format(__name__, field))
                continue

            if snapshot_value != current_value:
                fields_changed[field] = {
                    'old': snapshot_value,
                    'new': current_value
                }
        return fields_changed

    def _ondelta_dispatch_notifications(self):
        fields_changed = self._ondelta_get_differences()
        for field, changes in fields_changed.items():
            method_name = "ondelta_{}".format(field)
            if hasattr(self, method_name):
                getattr(self, method_name)(changes['old'], changes['new'])

        if fields_changed.keys():
            self.ondelta_all(fields_changed=fields_changed)

    def ondelta_all(self, fields_changed):
        """
        Child classes interested in executing logic based upon
        aggregate field changes should override this method
        """
        pass

    def save(self, *args, **kwargs):
        super_return = super(OnDeltaMixin, self).save(*args, **kwargs)
        self._ondelta_dispatch_notifications()
        self._ondelta_snapshot_state()
        return super_return
