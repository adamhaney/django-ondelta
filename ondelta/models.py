import copy
import pickle

from django.db import models
from django.utils.timezone import now


class DeltaNotifier(models.Model):
    _delta_notification_history = models.TextField(default='', null=True, editable=False)

    class Meta:
        abstract = True

    def __get_history(self):
        try:
            return pickle.loads(self._delta_notification_history)
        except:
            return []

    def __create_change_record(self):
        model_copy = copy.deepcopy(self)
        del model_copy._delta_notification_history

        return {
            'modified_time': now(),
            'model': model_copy
        }

    def __add_change_record(self):
        """
        Add a change record to the model's history
        """

        history = self.__get_history()
        history.append(self.__create_change_record())
        self._delta_notification_history = pickle.dumps(history)

    def _delta_fields_to_watch(self):
        return set(self._meta.get_all_field_names()) - set('_delta_notification_history')

    def _delta_catch_comparison_type_error(self, old_value, new_value):
        """
        This method gets called when a TypeError exception is thrown
        during a field comparison
        """
        pass

    def _delta_get_old_field_value(self, field):
        """
        Get the most recent previous value for a given field
        """
        return getattr(self.__get_history().pop()['model'], field)

    def _delta_get_new_field_value(self, field):
        """
        Get the current value of the field
        """
        return getattr(self, field)

    def _delta_compare_fields(self, field, old_value, new_value):
        """
        Compare old_value and new_value, you may want to override this
        depending on your definition of equality
        """
        return old_value != new_value

    def _delta_call_post_change(self, field, old_value, new_value):
        getattr(self, "{}_post_change".format(field))(old_value, new_value)

    def get_most_recent_historical_revision(self):
        return self.get_history().pop()

    def _delta_check_changes_and_notify(self):
        fields_changed = False

        for field in self._delta_fields_to_watch():
            try:
                old_value = self._delta_get_old_field_value(field)
                new_value = self._delta_get_new_field_value(field)
                if self._delta_compare_fields(field, old_value, new_value):
                    # If any fields have changed save a new
                    # revision (no need to duplicate the same data
                    # over and over again)
                    fields_changed = True
                    self._delta_call_post_change(field, old_value, new_value)
            except (AttributeError, ValueError):
                # Checkpoint more history if we're throwing an error
                fields_changed = True
        return fields_changed

    def save(self, *args, **kwargs):
        save_revision = False

        # If we don't have any history this is a new model, so we need
        # to save an initial copy to diff against
        if len(self.__get_history()) == 0:
            save_revision = True

        # If we do have history, diff against it and see if anything has changed
        else:
            save_revision = self._delta_check_changes_and_notify()

        if save_revision:
            self.__add_change_record()

        super(DeltaNotifier, self).save(*args, **kwargs)
