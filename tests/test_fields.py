# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation

from unittest import TestCase
from rest_orm import errors, fields, models


class FieldTestCase(TestCase):

    def test_deserialize_missing_value(self):
        """Test replacing a missing value with the specified default."""
        field = fields.Field('[key]', missing='value')
        value = field.deserialize({})
        self.assertTrue(value == 'value')


class BooleanTestCase(TestCase):

    def test_deserialize_value(self):
        field = fields.Boolean('[key]')
        value = field.deserialize({'key': 1})
        self.assertTrue(value is True)


class DateTestCase(TestCase):

    def test_deserialize_value(self):
        field = fields.Date('[key]')
        value = field.deserialize({'key': '2015-01-31'})
        self.assertTrue(value.year == 2015)
        self.assertTrue(value.month == 1)
        self.assertTrue(value.day == 31)

    def test_deserialize_formatted_value(self):
        field = fields.Date('[key]', date_format='%m/%d/%Y')
        value = field.deserialize({'key': '01/31/2015'})
        self.assertTrue(value.year == 2015)
        self.assertTrue(value.month == 1)
        self.assertTrue(value.day == 31)

    def test_deserialize_invalid_value(self):
        try:
            fields.Date('[key]').deserialize({'key': 'AB'})
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)


class DumpTestCase(TestCase):

    def test_deserialize_value(self):
        field = fields.Dump('value')
        value = field.deserialize({})
        self.assertTrue(value == 'value')


class DecimalTestCase(TestCase):

    def test_deserialize_value(self):
        field = fields.Decimal('[key]')
        value = field.deserialize({'key': '10.50'})
        self.assertTrue(value == Decimal('10.50'))

    def test_deserialize_invalid_value(self):
        try:
            fields.Decimal('[key]').deserialize({'key': 'AB'})
            self.assertTrue(False)
        except InvalidOperation:
            self.assertTrue(True)


class IntegerTestCase(TestCase):

    def test_deserialize_value(self):
        field = fields.Integer('[key]')
        value = field.deserialize({'key': '10'})
        self.assertTrue(value == 10)

    def test_deserialize_invalid_value(self):
        try:
            fields.Integer('[key]').deserialize({'key': 'AB'})
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)


class FunctionTestCase(TestCase):

    def test_adapted_function_deserialization(self):
        """Test deserializing function field."""
        field = fields.Function(lambda x: 'value', path='[x]')
        value = field.deserialize({'x': 'anything'})
        self.assertTrue(value == 'value')


class ListTestCase(TestCase):

    def test_deserialize_value(self):
        """Test deserializing list field."""
        field = fields.List('[x]')

        value = field.deserialize({'x': 1})
        self.assertTrue(value == [1])

        value = field.deserialize({'x': ['hi']})
        self.assertTrue(value == ['hi'])

    def test_deserialize_value_from_position(self):
        """Test deserializing a list item."""
        field = fields.Field('[1]')
        value = field.deserialize([1, 2, 3])
        self.assertTrue(value == 2)


class NestedTestCase(TestCase):

    def test_deserialize_value(self):
        """Test deserializing nested field."""
        class Test(models.Model):
            number = fields.Integer('[y]')

        field = fields.Nested(Test, path='[x]')
        value = field.deserialize({'x': {'y': 1}})
        self.assertTrue(isinstance(value, dict))
        self.assertIn('number', value)
        self.assertTrue(value['number'] == 1)


class StringTestCase(TestCase):

    def test_deserialize_value(self):
        """Test deserializing string field."""
        field = fields.String('[x]')

        value = field.deserialize({'x': 1})
        self.assertTrue(value == '1')

        value = field.deserialize({'x': True})
        self.assertTrue(value == 'True')
