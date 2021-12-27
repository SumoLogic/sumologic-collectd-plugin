# -*- coding: utf-8 -*-

_reserved_symbols = {
    " ": "_",
    "=": ":",
}


def validate_non_empty(value, key):
    if not value:
        raise Exception("Value for key %s cannot be empty" % key)


def validate_positive(value, key):
    if not value > 0:
        raise Exception("Value %s for key %s is not a positive number" % (value, key))


def validate_non_negative(value, key):
    if value < 0:
        raise Exception("Value %s for key %s is a negative number" % (value, key))


def validate_string_type(value, field, label1, label2):
    """
    Field must be string type
    """

    if not isinstance(value, str):
        raise Exception(
            "%s %s for %s %s must be string type. Type is %s"
            % (label1, value, label2, field, type(value))
        )


def validate_boolean_type(field, value):
    """
    Field must be string type
    """

    if not isinstance(value, bool):
        raise Exception(
            'Value for %s must be boolean type, but it was "%s"(%s)'
            % (field, value, type(value))
        )


def sanitize_field(value):
    """
    Field must be string that does not contains '=' or ' '
    """

    # Convert field to string
    value = str(value)

    for reserved_symbol, replacement in _reserved_symbols.items():
        if reserved_symbol in value:
            value = value.replace(reserved_symbol, replacement)
    return value


class RecoverableException(Exception):
    """
    Exception that are recoverable.
    """
