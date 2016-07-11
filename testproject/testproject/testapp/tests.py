# -*- coding: utf-8 -*-

from mock import Mock, patch, call

from django.test import TestCase

from django_dynamic_fixture import G, N

from .models import Foo, Bar


class OndeltaMethodCallUnitTests(TestCase):

    @patch('ondelta.models.OnDeltaMixin.ondelta_all')
    def setUp(self, ondelta_all_mock):

        self.ondelta_all_mock = ondelta_all_mock

        self.delta_model = Foo.objects.create(char_field='original_value')
        self.delta_model.ondelta_char_field = Mock()
        self.delta_model.char_field = 'second_value'
        self.delta_model.save()
        self.delta_model.char_field = 'third_value'

        # Save intentionally called twice here so we can test for idempotency
        self.delta_model.save()
        self.delta_model.save()

        # Intentionally not saved to test pre-save object state
        self.delta_model.char_field = 'fourth_value'

    def test_shadow_does_not_contain_unsaved_values(self):
        self.assertEqual(self.delta_model._ondelta_shadow.char_field, 'third_value')

    def test_get_differences(self):
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


class WorkFlowTests(TestCase):

    def setUp(self):
        self.foo = G(Foo, char_field='foo')

    def test_get_from_db(self):
        foo = Foo.objects.get(char_field='foo')
        foo.char_field = 'bar'
        foo.save()
        foo.char_field = 'baz'
        foo.save()
        self.assertEqual(foo.char_field_delta_count, 2)

    def test_create(self):
        foo = Foo.objects.create(char_field='foo')
        foo.char_field = 'bar'
        foo.save()
        foo.char_field = 'baz'
        foo.save()
        self.assertEqual(foo.char_field_delta_count, 2)

    def test_construct(self):
        foo = Foo(char_field='foo')
        foo.char_field = 'bar'
        foo.save()
        foo.char_field = 'baz'
        foo.save()
        self.assertEqual(foo.char_field_delta_count, 1)

    def test_g(self):
        foo = G(Foo, char_field='foo')
        foo.char_field = 'bar'
        foo.save()
        foo.char_field = 'baz'
        foo.save()
        self.assertEqual(foo.char_field_delta_count, 2)

    def test_n(self):
        foo = N(Foo, char_field='foo')
        foo.char_field = 'bar'
        foo.save()
        foo.char_field = 'baz'
        foo.save()
        self.assertEqual(foo.char_field_delta_count, 1)


class SaveChangesMadeByOndeltaMethodTests(TestCase):

    @patch('ondelta.models.OnDeltaMixin.ondelta_all')
    def setUp(self, ondelta_all_mock):

        self.ondelta_all_mock = ondelta_all_mock

        self.delta_model = Foo.objects.create(char_field='original_value')
        self.delta_model.char_field = 'second_value'
        self.delta_model.save()
        self.delta_model.char_field = 'third_value'

        # Save intentionally called twice here so we can test for idempotency
        self.delta_model.save()
        self.delta_model.save()

        # Intentionally not saved to test pre-save object state
        self.delta_model.char_field = 'fourth_value'

    def test_model_start_unmodified(self):
        self.assertEqual(Foo.objects.get().char_field_delta_count, 2)
        self.delta_model.save()
        self.assertEqual(Foo.objects.get().char_field_delta_count, 3)

    def test_dispatch_calls_ondelta_all_with_correct_args(self):
        self.ondelta_all_mock.assert_has_calls(
            [
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
                        'char_field_delta_count': {
                            'old': 0,
                            'new': 1,
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
                call(
                    fields_changed={
                        'char_field_delta_count': {
                            'old': 1,
                            'new': 2,
                        }
                    }
                ),
            ]
        )


class PostOnDeltaSignalTests(TestCase):

    def setUp(self):
        self.foo = Foo.objects.create(char_field='original_value')

    @patch('ondelta.signals.post_ondelta_signal.send')
    def test_signal_generated_with_correct_kwargs_on_any_delta(self, signal_mock):
        signal_mock.reset_mock()
        self.foo.char_field='second_value'
        self.foo.save()
        signal_mock.assert_called_once_with(
            fields_changed={
                'char_field': {
                    'old': 'original_value',
                    'new': 'second_value',
                }
            },
            instance=self.foo, 
            sender=Foo,
        )

    @patch('ondelta.signals.post_ondelta_signal.send')
    def test_signal_not_generated_when_no_changes(self, signal_mock):
        self.foo.save()
        self.assertFalse(signal_mock.called)


class SupportedRelatedFieldTypeTests(TestCase):

    def setUp(self):
        self.foo = Foo.objects.create()
        self.bar = Bar.objects.create()

    @patch('testproject.testapp.models.Bar.ondelta_foreign_key')
    def test_foreign_key(self, fk_mock):
        self.bar.foreign_key = self.foo
        self.bar.save()
        fk_mock.assert_called_once_with(None, self.foo)

    @patch('testproject.testapp.models.Bar.ondelta_one_to_one')
    def test_one_to_one(self, o2o_mock):
        self.bar.one_to_one = self.foo
        self.bar.save()
        o2o_mock.assert_called_once_with(None, self.foo)


class UnsupportedRelatedFieldTypeTests(TestCase):

    class add_mock_attr(object):

        def __init__(self, thing, attr_name):
            self.thing = thing
            self.attr_name = attr_name

        def __enter__(self):
            m = Mock()
            setattr(self.thing, self.attr_name, m)
            return m

        def __exit__(self, exc_type, exc_val, exc_tb):
            delattr(self.thing, self.attr_name)

    def setUp(self):
        self.foo = Foo.objects.create()
        self.bar = Bar.objects.create()

    def test_many_to_many(self):
        with self.add_mock_attr(Bar, 'ondelta_many_to_many') as m:
            self.bar.many_to_many.add(self.foo)
            self.bar.save()
            assert not m.called

    def test_foreign_key_reverse(self):
        with self.add_mock_attr(Foo, 'ondelta_foreign_key_reverse') as m:
            self.bar.foreign_key = self.foo
            self.bar.save()
            assert not m.called

    def test_one_to_one_reverse(self):
        with self.add_mock_attr(Foo, 'ondelta_one_to_one_reverse') as m:
            self.bar.one_to_one = self.foo
            self.bar.save()
            assert not m.called

    def test_many_to_many_reverse(self):
        with self.add_mock_attr(Foo, 'ondelta_many_to_many_reverse') as m:
            self.bar.many_to_many.add(self.foo)
            self.bar.save()
            assert not m.called
