# -*- coding: utf-8 -*-


class AdapterError(Exception):
    """Unreachable endpoint error."""

    def __init__(self, message):
        self.message = message
