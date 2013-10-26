from datetime import datetime

from mock import patch, call

from django.test import TestCase

from .models import TestDeltaModel


class DjangoNotifierHistoryTest(TestCase):

    @patch('ondelta.models.OnDeltaMixin._delta_call_ondelta_methods')
    def setUp(self, call_on_delta_mock):
        self.call_on_delta_mock = call_on_delta_mock

        self.delta_model = TestDeltaModel.objects.create(charfield='original_value')
        self.delta_model.charfield = 'second_value'
        self.delta_model.save()
        self.delta_model.charfield = 'third_value'
        self.delta_model.save()

        # Intentionally not saved to test pre-save object state
        self.delta_model.charfield = 'fourth_value'

    def test_history_original_value(self):
        self.assertEqual(
            self.delta_model._get_history()[0]['model'].charfield,
            'original_value',
        )

    def test_history_second_value(self):
        self.assertEqual(
            self.delta_model._get_history()[1]['model'].charfield,
            'second_value',
        )

    def test_history_third_value(self):
        self.assertEqual(
            self.delta_model._get_history()[2]['model'].charfield,
            'third_value',
        )

    def test_modified_time_exists(self):
        self.assertEqual(
            type(self.delta_model._get_history()[0]['modified_time']),
            datetime
        )

    def test_fields_to_watch_contains_fields(self):
        """
        Make sure we're not including id, or our own history field to
        trigger functions or pass to ondelta_all
        """

        self.assertEqual(
            self.delta_model._delta_fields_to_watch(), set(['intfield', 'charfield'])

        )

    def test_get_old_field_value(self):
        """
        The 'old' field value should be the one just before the
        current value ('fourth_value'), which would be 'third_value'
        """
        self.assertEqual(
            self.delta_model._delta_get_old_field_value('charfield'),
            'third_value'
        )

    def test_get_new_field_value(self):
        """
        _delta_get_new_field_value is basically just model.<field>
        we've named it to drive home the point that there's a
        difference between 'old_value' and 'new_value', where old is
        what it was before it was changed 'this time' (it's current
        value)
        """
        self.assertEqual(
            self.delta_model._delta_get_new_field_value('charfield'),
            'fourth_value'
        )

    def test_inequality(self):
        self.assertTrue(
            self.delta_model._delta_ne_fields(
                'charfield',
                self.delta_model._delta_get_old_field_value('charfield'),
                self.delta_model._delta_get_new_field_value('charfield')
            )
        )

    def test_save_brings_equality(self):
        """
        After save is called on a model if no more modifications are
        made then 'new' and 'old' are the same
        """
        self.delta_model.save()
        self.assertFalse(
            self.delta_model._delta_ne_fields(
                'charfield',
                self.delta_model._delta_get_old_field_value('charfield'),
                self.delta_model._delta_get_new_field_value('charfield')
            )
        )

    def test_calling_ondelta_correctly(self):
        self.call_on_delta_mock.assert_has_calls(
            [
                call('charfield', 'original_value', 'second_value'),
                call('charfield', 'second_value', 'third_value')
            ]
       )
