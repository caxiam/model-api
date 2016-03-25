# -*- coding: utf-8 -*-
from unittest import TestCase

from rest_orm import errors, fields, models


class FieldsTestCase(TestCase):

    def test_deserialize_deeply_nested_field(self):
        """Test deserializing a heavily nested field."""
        field = fields.AdaptedField('[x][y][z]')
        value = field.deserialize({'x': {'y': {'z': 'value'}}})
        self.assertTrue(value == 'value')

    def test_deserialize_list_item(self):
        """Test deserializing a list item."""
        field = fields.AdaptedField('[1]')
        value = field.deserialize([1, 2, 3])
        self.assertTrue(value == 2)

    def test_validate_disallow_missing(self):
        """Test validating a missing value when allow_missing is `False`."""
        field = fields.AdaptedField('[x]', allow_missing=False)
        try:
            field.deserialize({'z': 1})
            self.assertTrue(False)
        except KeyError:
            self.assertTrue(True)

    def test_replace_missing_value(self):
        """Test replacing a missing value with the specified default."""
        field = fields.AdaptedField('[key]', missing='value')
        value = field.deserialize({'x': 1})
        self.assertTrue(value == 'value')

    def test_validate_deserialized_value(self):
        """Test validating a deserialized value."""
        def validate_input(value):
            if value > 10:
                return
            raise errors.AdapterError('Invalid value.')

        field = fields.AdaptedField('[x]', validate=validate_input)
        try:
            field.deserialize({'x': 5})
            self.assertTrue(False)
        except errors.AdapterError:
            self.assertTrue(True)

        value = field.deserialize({'x': 11})
        self.assertTrue(value == 11)

    def test_adapted_boolean_deserialization(self):
        """Test deserializing boolean field."""
        field = fields.AdaptedBoolean('[x]')

        value = field.deserialize({'x': 1})
        self.assertTrue(value is True)

        value = field.deserialize({'x': 'hello'})
        self.assertTrue(value is True)

        value = field.deserialize({'x': True})
        self.assertTrue(value is True)

        value = field.deserialize({'x': 0})
        self.assertTrue(value is False)

        value = field.deserialize({'x': ''})
        self.assertTrue(value is False)

        value = field.deserialize({'x': None})
        self.assertTrue(value is False)

    def test_adapted_date_deserialization(self):
        """Test deserializing date field."""
        field = fields.AdaptedDate('[x]')
        value = field.deserialize({'x': '2015-01-01'})
        self.assertTrue(value.year == 2015)
        self.assertTrue(value.month == 1)
        self.assertTrue(value.day == 1)

        field = fields.AdaptedDate('[x]', date_format='%m/%d/%Y')
        value = field.deserialize({'x': '01/01/2015'})
        self.assertTrue(value.year == 2015)
        self.assertTrue(value.month == 1)
        self.assertTrue(value.day == 1)

    def test_adapted_decimal_deserialization(self):
        """Test deserializing decimal field."""
        from decimal import Decimal

        field = fields.AdaptedDecimal('[x]')
        value = field.deserialize({'x': '12.50'})

        self.assertTrue(value == 12.50)
        self.assertTrue(isinstance(value, Decimal))

    def test_adapted_integer_deserialization(self):
        """Test deserializing integer field."""
        field = fields.AdaptedInteger('[x]')
        value = field.deserialize({'x': '1'})
        self.assertTrue(value == 1)

    def test_adapted_function_deserialization(self):
        """Test deserializing function field."""
        field = fields.AdaptedFunction(lambda x: 'value', path='[x]')
        value = field.deserialize({'x': 'anything'})
        self.assertTrue(value == 'value')

    def test_adapted_list_deserialization(self):
        """Test deserializing list field."""
        field = fields.AdaptedList('[x]')

        value = field.deserialize({'x': 1})
        self.assertTrue(value == [1])

        value = field.deserialize({'x': ['hi']})
        self.assertTrue(value == ['hi'])

    def test_adapted_nested_deserialization(self):
        """Test deserializing nested field."""
        class Test(models.AdaptedModel):
            number = fields.AdaptedInteger('[y]')

        field = fields.AdaptedNested(Test, path='[x]')
        value = field.deserialize({'x': {'y': 1}})
        self.assertTrue(isinstance(value, Test))
        self.assertTrue(value.number == 1)

    def test_adapted_string_deserialization(self):
        """Test deserializing string field."""
        field = fields.AdaptedString('[x]')

        value = field.deserialize({'x': 1})
        self.assertTrue(value == '1')

        value = field.deserialize({'x': True})
        self.assertTrue(value == 'True')
