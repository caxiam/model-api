# -*- coding: utf-8 -*-
from unittest import TestCase

from rest_orm import fields, models


class TestModel(models.AdaptedModel):
    first = fields.AdaptedString('[first]')
    address1 = fields.AdaptedString('[address][address][0]')
    address2 = fields.AdaptedString('[address][address][1]')
    city = fields.AdaptedString('[address][city]')

    def make_request(self):
        return '{"first": "First Name"}'

    def post_load(self):
        self.full_name = '{} Last Name'.format(self.first)


class ModelTestCase(TestCase):

    def test_model_connect(self):
        """Test loading the response from the connect method."""
        model = TestModel().connect()
        self.assertTrue(model.first == 'First Name')

    def test_model_loads(self):
        """Test loading the json from the loads method."""
        model = TestModel().loads('{"first": "First Name"}')
        self.assertTrue(model.first == 'First Name')

    def test_model_load(self):
        """Test loading the python object from the load method."""
        model = TestModel().load({"first": "First Name"})
        self.assertTrue(model.first == 'First Name')

    def test_model_post_load(self):
        """Test post-load actions created from the post_load method."""
        model = TestModel().load({"first": "First Name"})
        self.assertTrue(model.full_name == 'First Name Last Name')

    def test_model_dump(self):
        """Test serialized a dictionary into the specified field paths."""
        expected = {
            'first': 'Test',
            'address': {
                'city': 'Arden',
                'address': ['100 Harvard Street', '#801B']
            }
        }
        actual = TestModel().dump({
            'first': 'Test',
            'address1': '100 Harvard Street',
            'address2': '#801B',
            'city': 'Arden'
        })
        self.assertTrue(actual == expected)
