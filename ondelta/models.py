import copy
import pickle

from django.db import models
from django.utils.timezone import now


class OnDeltaMixin(models.Model):
    _delta_notification_history = models.TextField(default='', null=True, editable=False)

    class Meta:
        abstract = True

    def _get_history(self):
        try:
            return pickle.loads(self._delta_notification_history)
        except:
            return []

    def _get_current_time(self):
        """
        This method exists to make test stubbing easier
        """
        return now()

    def __create_change_record(self):
        model_copy = copy.deepcopy(self)
        del model_copy._delta_notification_history

        return {
            'modified_time': self._get_current_time(),
            'model': model_copy
        }

    def __add_change_record(self):
        """
        Add a change record to the model's history
        """

        history = self._get_history()
        history.append(self.__create_change_record())
        self._delta_notification_history = pickle.dumps(history)

    def _delta_fields_to_watch(self):
        return set(self._meta.get_all_field_names()) - set(['id', 'c', '_delta_notification_history'])

    def _delta_get_old_field_value(self, field):
        """
        Get the most recent previous value for a given field
        """
        return getattr(self._get_history().pop()['model'], field)

    def _delta_get_new_field_value(self, field):
        """
        Get the current value of the field
        """
        return getattr(self, field)

    def _delta_ne_fields(self, field, old_value, new_value):
        """
        Notifications are sent that a field changed when two fields
        that are compared to one another evalue to be unequal. This
        method evaluates whether or not two fields are equal, you may
        wish to override this depending upon your application's view
        of inequality.
        """
        return old_value != new_value

    def _delta_call_ondelta_methods(self, field, old_value, new_value):
        getattr(self, "ondelta_{}".format(field))(old_value, new_value)

    def _delta_check_changes_and_notify(self):
        fields_changed = False

        for field in self._delta_fields_to_watch():
            old_value = self._delta_get_old_field_value(field)
            new_value = self._delta_get_new_field_value(field)
            if self._delta_compare_fields(field, old_value, new_value):
                # If any fields have changed save a new
                # revision (no need to duplicate the same data
                # over and over again)
                fields_changed = True
                self._delta_call_ondelta_methods(field, old_value, new_value)

        return fields_changed

    def save(self, *args, **kwargs):
        # We don't always want to save a revision if the model hasn't
        # changed, so start from the default position that a revision
        # should not be created
        save_revision = False

        # If we don't have any history this is a new model, so we need
        # to save an initial copy to diff against
        if len(self._get_history()) == 0:
            save_revision = True

        # If we do have history, diff against it and see if anything has changed
        else:
            save_revision = self._delta_check_changes_and_notify()

        # Always save *after* we've check for changes
        if save_revision:
            self.__add_change_record()

        # Call super on save so we persist
        # NOTE: this means if the parent save fails then we could
        # accidentally send multiple notifications
        return super(OnDeltaMixin, self).save(*args, **kwargs)
