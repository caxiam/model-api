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
            raw_value = self.map_from_string(self.path, data)
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
