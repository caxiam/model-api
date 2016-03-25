# -*- coding: utf-8 -*-


class ModelRegistry(type):
    registry = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.registry[name] = new_cls
        return new_cls


def get_class(name):
    return ModelRegistry.registry[name]
