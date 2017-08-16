# -*- coding: utf-8 -*-

_reserved_symbols = frozenset([' ', '='])


def validate_non_empty(s, key):
    if not s:
        raise Exception('Value for key %s cannot be empty' % key)


def validate_positive(v, key):
    if not v > 0:
        raise Exception('Value %s for key %s is not a positive number' % (v, key))


def validate_non_negative(v, key):
    if v < 0:
        raise Exception('Value %s for key %s is a negative number' % (v, key))


def validate_string_type(s, f, l1, l2):
    """
    Field must be string type
    """

    if type(s) is not str:
        raise Exception('%s %s for %s %s must be string type. Type is %s' %
                        (l1, s, l2, f, type(s)))


def validate_field(s, f, l1, l2):
    """
    Field must be string that does not contains '=' or ' '
    """

    validate_string_type(s, f, l1, l2)

    for reserved_symbol in _reserved_symbols:
        if reserved_symbol in s:
            raise Exception('%s %s for %s %s must not contain reserved symbol \"%s\"' %
                            (l1, s, l2, f, reserved_symbol))


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

    pass
