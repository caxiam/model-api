# -*- coding: utf-8 -*-
from rest_orm.fields import AdaptedField
from rest_orm.utils import ModelRegistry

import json


class BaseModel(object):
    """Base model class responsible for registering child classes."""

    __metaclass__ = ModelRegistry


class AdaptedModel(BaseModel):
    """A flat representation of a single remote endpoint."""

    def connect(self, *args, **kwargs):
        """Make a request to a remote endpoint and load its JSON response."""
        response = self.make_request(*args, **kwargs)
        return self.loads(response)

    def loads(self, response):
        """Marshal a JSON response object into the model."""
        return self.load(json.loads(response))

    def load(self, response):
        """Marshal a python dictionary object into the model."""
        self._do_load(response)
        self.post_load()
        return self

    def dump(self, data):
        """Structure a flat dictionary into a nested output."""
        response = {}
        for field_name, value in data.iteritems():
            field = getattr(self, field_name)
            if not isinstance(field, AdaptedField):
                continue
            response = field.serialize(value, response)
        return response

    def post_load(self):
        """Perform any model level actions after load."""
        pass

    def _do_load(self, data):
        for field_name in dir(self):
            field = getattr(self, field_name)
            if not isinstance(field, AdaptedField):
                continue
            setattr(self, field_name, field.deserialize(data))

    def make_request(self):
        """Return the response data of a remote endpoint."""
        raise NotImplementedError
