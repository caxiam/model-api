# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal as PyDecimal

from rest_orm.utils import get_class


class Field(object):
    """Flat representaion of remote endpoint's field.

    `Field` and its child classes are self-destructive.  Once
    deserialization is complete, the instance is replaced by the typed
    value retrieved.
    """

    def __init__(self, path, missing=None):
        """Key extraction strategy and settings.

        :param path: A formattable string path.
        :param missing: The default deserialization value.
        """
        self.path = path
        self.missing = missing

    def deserialize(self, data):
        """Extract a value from the provided data object.

        :param data: A dictionary object.
        """
        if self.path is None:
            return self._deserialize(data)

        try:
            value = self.map_from_string(self.path, data)
        except (KeyError, IndexError):
            value = self.missing
        if value is None:
            return value
        return self._deserialize(value)

    def _deserialize(self, value):
        return value

    def map_from_string(self, path, data):
        """Return nested value from the string path taken.

        :param path: A string path to the value.  E.g. [name][first][0].
        :param data: A dictionary object.
        """
        def extract_by_type(path):
            try:
                return data[int(path)]
            except ValueError:
                return data[path]

        for path in path[1:-1].split(']['):
            data = extract_by_type(path)
        return data


class Boolean(Field):
    """Parse an adapted field into the boolean type."""

    def _deserialize(self, value):
        return bool(value)


class Date(Field):
    """Parse an adapted field into the datetime type."""

    def __init__(self, *args, **kwargs):
        self.date_format = kwargs.pop('date_format', '%Y-%m-%d')
        super(Date, self).__init__(*args, **kwargs)

    def _deserialize(self, value):
        return datetime.strptime(value, self.date_format)


class Dump(Field):
    """Return a pre-determined value."""

    def __init__(self, value):
        self.value = value

    def deserialize(self, data):
        return self.value


class Decimal(Field):
    """Parse an adapted field into the decimal type."""

    def _deserialize(self, value):
        return PyDecimal(value)


class Integer(Field):
    """Parse an adapted field into the integer type."""

    def _deserialize(self, value):
        return int(value)


class Function(Field):
    """Parse an adapted field into a specified function's output."""

    def __init__(self, f, *args, **kwargs):
        self.f = f
        super(Function, self).__init__(*args, **kwargs)

    def _deserialize(self, value):
        return self.f(value)


class List(Field):
    """Parse an adapted field into the list type."""

    def _deserialize(self, value):
        if not isinstance(value, list):
            return [value]
        return value


class Nested(Field):
    """Parse an adatped field into the Model type."""

    def __init__(self, model, *args, **kwargs):
        """Parse a list of nested objects into an Model.

        :param model: Model name or reference.
        """
        self.nested_model = model
        super(Nested, self).__init__(*args, **kwargs)

    @property
    def model(self):
        """Return an Model reference."""
        if isinstance(self.nested_model, str):
            return get_class(self.nested_model)
        return self.nested_model

    def _deserialize(self, value):
        if isinstance(value, list):
            return [self.model().load(val) for val in value]
        return self.model().load(value)


class String(Field):
    """Parse an adapted field into the string type."""

    def _deserialize(self, value):
        return str(value)
