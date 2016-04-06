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
        """Return `True` if the provided key can be parsed as an integer."""
        try:
            int(key)
            return True
        except ValueError:
            return False

    def _build_from_keys(self, keys, value):
        """Build the data structure bottom up from a set of keys."""
        # Reversing the keys is important because it allows us to
        # naively wrap values with the desired data-type.  We don't
        # worry about what key to assign to.
        for key in reversed(keys):
            # If the key is an integer, the value needs to be enclosed
            # in a list, otherwise it is enclosed in a dictionary
            if self._is_integer(key):
                # Because position is important for some APIs, we need
                # to pad out the list up to the point the key is
                # supposed to be position.
                response = []
                while len(response) < int(key):
                    response.append(None)
                # We append the value at its appropriate list position.
                response.append(value)
                value = response
            else:
                value = {key: value}
        return value

    def _assign_to_position(self, position, value, array, keys=[]):
        """Assign a value to its specified list position."""
        if position < 0:
            # We do not support assigning to the end of a list.
            # Because the "end" of the list is entirely based on the
            # operation's processing order, negatives are excluded from
            # serialized.
            raise ValueError('Invalid serialization position.')

        # Pad the list up to, and including, the specified list
        # position.  This is important because this method does not
        # append values to lists.  It instead assigns or updates
        # existing values to the new value.
        while len(array) < position + 1:
            array.append(None)

        # If the `array_value` is a padded value, we can replace it
        # without caring about its existing value.
        array_value = array[position]
        if array_value is not None:
            # If the value is a dictionary, we can update the dictionary
            # with a new key, value pair.  Any other value would require
            # us to overwrite data.
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
                # Dictionaries can not have integer keys.
                raise ValueError('Object is not list-like.')
            elif key in obj:
                if len(keys) == 1:
                    # If the key is in the object but is also the last key
                    # available for traversal, then an overwrite would be
                    # necessary to continue.
                    raise ValueError('Invalid serialization target.')
                # Recursively call the function, trimming the used key,
                # and descending into the object by the current key.
                obj = {key: self._assign_from_keys(value, keys[1:], obj[key])}
                return obj
            else:
                # If the key is not present in the dictionary, we can
                # update the dictionary with a new set of values without
                # worrying about overwriting data.
                obj.update(self._build_from_keys(keys, value))
                return obj
        elif isinstance(obj, list):
            if self._is_integer(key):
                # Lists terminate recursive execution.  However, the
                # `_assign_to_postition` method may call the
                # `_assign_from_keys` method if the object contains a
                # dictionary value at the specified position.
                return self._assign_to_position(int(key), value, obj, keys[1:])
            else:
                # List positions are not string like.  Someone goofed.
                raise ValueError('Invalid serialization target.')
        elif obj is None:
            # `None` type values are overwritten.
            obj = self._build_from_keys(keys, value)
            return obj
        else:
            # Some value occupies the desired position.
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
