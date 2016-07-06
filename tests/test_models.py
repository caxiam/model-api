# -*- coding: utf-8 -*-
from unittest import TestCase

from rest_orm import fields, models


class TestModel(models.Model):
    first = fields.String('[first]')

    def make_request(self):
        return '{"first": "First Name"}'

    def post_load(self, data):
        data['full_name'] = '{} Last Name'.format(data['first'])
        return data


class ModelTestCase(TestCase):

    def test_model_connect(self):
        """Test loading the response from the connect method."""
        result = TestModel().connect()
        self.assertTrue(result['first'] == 'First Name')

    def test_model_loads(self):
        """Test loading the json from the loads method."""
        result = TestModel().loads('{"first": "First Name"}')
        self.assertTrue(result['first'] == 'First Name')

    def test_model_load(self):
        """Test loading the python object from the load method."""
        result = TestModel().load({"first": "First Name"})
        self.assertTrue(result['first'] == 'First Name')

    def test_model_post_load(self):
        """Test post-load actions created from the post_load method."""
        result = TestModel().load({"first": "First Name"})
        self.assertTrue(result['full_name'] == 'First Name Last Name')
