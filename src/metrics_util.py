import collectd
import threading

class MetricsUtil:

    _reserved_symbols = [' ', '=']
    # reserved keywords are case-insensitive
    _reserved_keywords = ['_sourcehost', '_sourcename', '_sourcecategory', '_collectorid',
                          '_collector', '_source', '_sourceid', '_contenttype', '_rawname']

    @staticmethod
    def validate_nonempty(s, key):

        if not s:
            raise Exception('Value for key %s cannot be empty' % key)


    @staticmethod
    def validate_positive(v):

        if not v > 0:
            raise Exception('%s is not a positive float' % v)

    @staticmethod
    def validate_field(s):
        """
        Field must be string that does not contains '=' or ' '
        """

        if type(s) is not str:
            raise Exception('Field %s must be string type. Type is %s' % (s, type(s)))

        for reserved_symbol in MetricsUtil._reserved_symbols:
            if reserved_symbol in s:
                raise Exception('Field %s must not contain reserved symbol %s' %
                                (s, reserved_symbol))

    @staticmethod
    def validate_type(data, types):
        """
        Validate type are defined in types.db and matching data values
        """

        # Verify type is defined in types.db
        if data.type not in types:
            collectd.warning('write_callback: do not know how to handle type %s. '
                             'Do you have all your types.db files configured?' % data.type)
            return False

        # Verify values conform to the type defined
        if len(data.values) != len(types[data.type]):
            collectd.warning('write_callback: # values is different from type %s' % data.type)
            return False

        return True

    @staticmethod
    def start_timer(interval, func):
        """
        Start a thread to periodically run task func
        """

        timer = threading.Timer(interval, MetricsUtil.start_timer, args=[interval, func])
        timer.daemon = True
        timer.start()
        func()

    @staticmethod
    def fail_with_recoverable_exception(msg, e):
        """
        Warn about exception and raise RecoverableException
        """

        collectd.warning(msg + ': %s' % e.message)
        raise RecoverableException(e)

    @staticmethod
    def fail_with_unrecoverable_exception(msg, e):
        """
        Error about exception and pass through exception
        """

        collectd.error(msg + ': %s' % e.message)
        raise e


class RecoverableException(Exception):
    """
    Exception that are recoverable.
    """

    pass
