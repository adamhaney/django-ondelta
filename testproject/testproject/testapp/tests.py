from mock import Mock, patch, call

from django.test import TestCase

from .models import TestDeltaModel


class OndeltaMethodCallTests(TestCase):

    @patch('ondelta.models.OnDeltaMixin.ondelta_all')
    def setUp(self, ondelta_all_mock):
        self.ondelta_all_mock = ondelta_all_mock

        self.delta_model = TestDeltaModel.objects.create(char_field='original_value')
        self.delta_model.ondelta_char_field = Mock()
        self.delta_model.char_field = 'second_value'
        self.delta_model.save()
        self.delta_model.char_field = 'third_value'

        # Save intentionally called twice here so that dispatch method
        # tests test for idempotency
        self.delta_model.save()
        self.delta_model.save()

        # Intentionally not saved to test pre-save object state
        self.delta_model.char_field = 'fourth_value'

    def test_model_start_unmodified(self):
        """
        The constructor of our model saves a copy of the starting
        state, let's check that before save these aren't the same
        """
        self.assertEqual(self.delta_model._ondelta_shadow.char_field, 'third_value')

    def test_fields_changed(self):
        self.assertEqual(
            self.delta_model._ondelta_get_differences(),
            {
                'char_field': {
                    'old': 'third_value',
                    'new': 'fourth_value',
                }
            }
        )

    def test_dispatch_calls_single_methods_with_correct_args(self):
        self.delta_model.ondelta_char_field.assert_has_calls(
            [
                call('original_value', 'second_value'),
                call('second_value', 'third_value')
            ]
        )

    def test_dispatch_calls_ondelta_all_with_correct_args(self):
        self.ondelta_all_mock.assert_has_calls(
            [
                call(
                    fields_changed={
                        'char_field': {
                            'old': 'original_value',
                            'new': 'second_value'
                        }
                    }
                ),
                call(
                    fields_changed={
                        'char_field': {
                            'old': 'second_value',
                            'new': 'third_value'
                        }
                    }
                ),
            ]
        )


class SaveInsideOndeltaMethodTests(TestCase):

    @patch('ondelta.models.OnDeltaMixin.ondelta_all')
    def setUp(self, ondelta_all_mock):
        self.ondelta_all_mock = ondelta_all_mock

        self.delta_model = TestDeltaModel.objects.create(char_field='original_value')
        self.delta_model.char_field = 'second_value'
        self.delta_model.save()
        self.delta_model.char_field = 'third_value'

        # Save intentionally called twice here so that dispatch method
        # tests test for idempotency
        self.delta_model.save()
        self.delta_model.save()

        # Intentionally not saved to test pre-save object state
        self.delta_model.char_field = 'fourth_value'

    def test_model_start_unmodified(self):
        self.assertEqual(TestDeltaModel.objects.get().int_field, 2)
        self.delta_model.save()
        self.assertEqual(TestDeltaModel.objects.get().int_field, 3)

    def test_dispatch_calls_ondelta_all_with_correct_args(self):
        self.ondelta_all_mock.assert_has_calls(
            [
                call(
                    fields_changed={
                        'int_field': {
                            'old': 0,
                            'new': 1,
                        }
                    }
                ),
                call(
                    fields_changed={
                        'char_field': {
                            'old': 'original_value',
                            'new': 'second_value',
                        }
                    }
                ),
                call(
                    fields_changed={
                        'int_field': {
                            'old': 1,
                            'new': 2,
                        }
                    }
                ),
                call(
                    fields_changed={
                        'char_field': {
                            'old': 'second_value',
                            'new': 'third_value',
                        }
                    }
                ),
            ]
        )
