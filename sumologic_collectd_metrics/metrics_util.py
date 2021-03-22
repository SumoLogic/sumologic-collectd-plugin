# -*- coding: utf-8 -*-

_reserved_symbols = {
    ' ': None,
    '=': ':',
}


def validate_non_empty(value, key):
    if not value:
        raise Exception('Value for key %s cannot be empty' % key)


def validate_positive(value, key):
    if not value > 0:
        raise Exception('Value %s for key %s is not a positive number' % (value, key))


def validate_non_negative(value, key):
    if value < 0:
        raise Exception('Value %s for key %s is a negative number' % (value, key))


def validate_string_type(value, field, label1, label2):
    """
    Field must be string type
    """

    if not isinstance(value, str):
        raise Exception('%s %s for %s %s must be string type. Type is %s' %
                        (label1, value, label2, field, type(value)))


def validate_field(value, field, label1, label2):
    """
    Field must be string that does not contains '=' or ' '
    """

    # Convert field to string
    value = str(value)

    for reserved_symbol, replacement in _reserved_symbols.items():
        if reserved_symbol in value:
            if replacement is None:
                raise Exception('%s %s for %s %s must not contain reserved symbol \"%s\"' %
                                (label1, value, label2, field, reserved_symbol))

            value = value.replace(reserved_symbol, replacement)
    return value


def validate_type(data, types):
    """
    Validate type are defined in types.db and matching data values
    """

    # Verify type is defined in types.db
    if data.type not in types:
        raise Exception('Do not know how to handle type %s. Do you have all your types.db files'
                        ' configured?' % data.type)

    # Verify values conform to the type defined
    if len(data.values) != len(types[data.type]):
        raise Exception('Number values %s differ from types defined for %s' %
                        (data.values, data.type))


class RecoverableException(Exception):
    """
    Exception that are recoverable.
    """
