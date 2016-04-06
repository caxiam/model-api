# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal

from rest_orm.utils import get_class


class AdaptedField(object):
    """Flat representaion of remote endpoint's field.

    `AdaptedField` and its child classes are self-destructive.  Once
    deserialization is complete, the instance is replaced by the typed
    value retrieved.
    """

    def __init__(self, path, missing=None, nullable=True, required=False,
                 validate=None):
        """Key extraction strategy and settings.

        :param path: A formattable string path.
        :param missing: The default deserialization value.
        :param nullable: If `False`, disallow `None` type values.
        :param required: If `True`, raise an error if the key is missing.
        :param validate: A callable object.
        """
        self.path = path
        self.missing = missing
        self.nullable = nullable
        self.required = required
        self.validate = validate

    def deserialize(self, data):
        """Extract a value from the provided data object.

        :param data: A dictionary object.
        """
        if self.path is None:
            return self._deserialize(data)

        try:
            raw_value = self._map_from_string(self.path, data)
        except (KeyError, IndexError):
            if self.required:
                raise KeyError('{} not found.'.format(self.path))
            value = self.missing
        else:
            if raw_value is None and self.nullable:
                value = None
            else:
                value = self._deserialize(raw_value)

        self._validate(value)
        return value

    def _deserialize(self, value):
        return value

    def _validate(self, value):
        if self.validate is not None:
            self.validate(value)
        return None

    def _map_from_string(self, path, data):
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

    def serialize(self, value, obj={}):
        """Using `path`, structure an object into the required output."""
        if self.path is None:
            raise ValueError('Value can not be serialized.')
        return self._assign_from_keys(value, self.path[1:-1].split(']['), obj)

    def _is_integer(self, key):
        """Determine if the key is an integer."""
        try:
            int(key)
            return True
        except ValueError:
            return False

    def _build_from_keys(self, keys, value):
        """Build the data structure bottom up from a set of keys."""
        for key in reversed(keys):
            if self._is_integer(key):
                response = []
                while len(response) < int(key):
                    response.append(None)
                response.append(value)
                value = response
            else:
                value = {key: value}
        return value

    def _assign_to_position(self, position, value, array, keys=[]):
        """Assign a value to its specified list position."""
        if position < 0:
            raise ValueError('Invalid serialization position.')

        while len(array) < position + 1:
            array.append(None)

        array_value = array[position]
        if array_value is not None:
            if isinstance(array_value, dict):
                array = [self._assign_from_keys(value, keys, array_value)]
            else:
                raise ValueError('Position occupied.')
        else:
            array[position] = self._build_from_keys(keys, value)

        return array

    def _assign_from_keys(self, value, keys=[], obj={}):
        """Get or create a key, value pair."""
        key = keys[0]
        if isinstance(obj, dict):
            if self._is_integer(key):
                raise ValueError('Object is not list-like.')
            elif key in obj:
                if len(keys) == 1:
                    raise ValueError('Invalid serialization target.')
                obj = {key: self._assign_from_keys(value, keys[1:], obj[key])}
                return obj
            else:
                obj.update(self._build_from_keys(keys, value))
                return obj
        elif isinstance(obj, list):
            if self._is_integer(key):
                return self._assign_to_position(int(key), value, obj, keys[1:])
            else:
                raise ValueError('Invalid serialization target.')
        elif obj is None:
            obj = self._build_from_keys(keys, value)
            return obj
        else:
            raise ValueError('Invalid serialization target.')


class AdaptedBoolean(AdaptedField):
    """Parse an adapted field into the boolean type."""

    def _deserialize(self, value):
        return bool(value)


class AdaptedDate(AdaptedField):
    """Parse an adapted field into the datetime type."""

    def __init__(self, *args, **kwargs):
        self.date_format = kwargs.pop('date_format', '%Y-%m-%d')
        super(AdaptedDate, self).__init__(*args, **kwargs)

    def _deserialize(self, value):
        return datetime.strptime(value, self.date_format)


class AdaptedDecimal(AdaptedField):
    """Parse an adapted field into the decimal type."""

    def _deserialize(self, value):
        return Decimal(value)


class AdaptedInteger(AdaptedField):
    """Parse an adapted field into the integer type."""

    def _deserialize(self, value):
        return int(value)


class AdaptedFunction(AdaptedField):
    """Parse an adapted field into a specified function's output."""

    def __init__(self, f, *args, **kwargs):
        self.f = f
        super(AdaptedFunction, self).__init__(*args, **kwargs)

    def _deserialize(self, value):
        return self.f(value)


class AdaptedList(AdaptedField):
    """Parse an adapted field into the list type."""

    def _deserialize(self, value):
        if not isinstance(value, list):
            return [value]
        return value


class AdaptedNested(AdaptedField):
    """Parse an adatped field into the AdaptedModel type."""

    def __init__(self, model, *args, **kwargs):
        """Parse a list of nested objects into an AdaptedModel.

        :param model: AdaptedModel name or reference.
        """
        self.nested_model = model
        super(AdaptedNested, self).__init__(*args, **kwargs)

    @property
    def model(self):
        """Return an AdaptedModel reference."""
        if isinstance(self.nested_model, str):
            return get_class(self.nested_model)
        return self.nested_model

    def _deserialize(self, value):
        if isinstance(value, list):
            return [self.model().load(val) for val in value]
        return self.model().load(value)


class AdaptedString(AdaptedField):
    """Parse an adapted field into the string type."""

    def _deserialize(self, value):
        return str(value)
