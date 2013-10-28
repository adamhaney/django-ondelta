from mock import Mock, patch, call

from django.test import TestCase

from .models import TestDeltaModel


class DjangoNotifierHistoryTest(TestCase):

    @patch('ondelta.models.OnDeltaMixin.ondelta_all')
    def setUp(self, ondelta_all_mock):
        self.ondelta_all_mock = ondelta_all_mock

        self.delta_model = TestDeltaModel.objects.create(charfield='original_value')
        self.delta_model.ondelta_charfield = Mock()
        self.delta_model.charfield = 'second_value'
        self.delta_model.save()
        self.delta_model.charfield = 'third_value'

        # Save intentionally called twice here so that dispatch method
        # tests test for idempotency
        self.delta_model.save()
        self.delta_model.save()

        # Intentionally not saved to test pre-save object state
        self.delta_model.charfield = 'fourth_value'

    def test_model_start_unmodified(self):
        """
        The constructor of our model saves a copy of the starting
        state, let's check that before save these aren't the same
        """
        self.assertEqual(self.delta_model.model_snapshot.charfield, 'third_value')

    def test_fields_changed(self):
        self.assertEqual(
            self.delta_model._ondelta_get_differences(),
            {
                'charfield':
                    {'old': 'third_value', 'new': 'fourth_value'}
            }
        )

    def test_dispatch_calls_single_methods_with_correct_args(self):
        self.delta_model.ondelta_charfield.assert_has_calls(
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
                        'charfield': {
                            'old': 'original_value',
                            'new': 'second_value'
                        }
                    }
               ),
                call(
                    fields_changed={
                        'charfield': {
                            'old': 'second_value',
                            'new': 'third_value'
                        }
                    }
               )
            ]
        )
                
