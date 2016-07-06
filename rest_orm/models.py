# -*- coding: utf-8 -*-
from rest_orm.fields import Field
from rest_orm.utils import ModelRegistry

import json


class BaseModel(object):
    """Base model class responsible for registering child classes."""

    __metaclass__ = ModelRegistry


class Model(BaseModel):
    """A flat representation of a single remote endpoint."""

    def loads(self, data):
        """Load a JSON string to a flattened dictionary."""
        return self.load(json.loads(data))

    def load(self, data):
        """Flatten a nested dictionary."""
        response = {}
        for field_name in dir(self):
            field = getattr(self, field_name)
            if not isinstance(field, Field):
                continue
            response[field_name] = field.deserialize(data)

        response = self.post_load(response)
        return response

    def connect(self, *args, **kwargs):
        """Make a request to a remote endpoint and load its JSON response."""
        response = self.make_request(*args, **kwargs)
        return self.loads(response)

    def post_load(self, data):
        """Perform any model level actions after load."""
        return data

    def make_request(self):
        """Return the response data of a remote endpoint."""
        raise NotImplementedError
