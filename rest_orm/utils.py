# -*- coding: utf-8 -*-


class ModelRegistry(type):
    """Meta class for used to register classes within the registry."""

    registry = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.registry[name] = new_cls
        return new_cls


def get_class(name):
    """Return class reference from class name."""
    return ModelRegistry.registry[name]
