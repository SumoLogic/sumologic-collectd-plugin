class Constants:
    host='test_host'
    plugin='test_plugin'
    plugin_instance='test_plugin_instance'
    type='test_type'
    type_instance='test_type_instance'
    meta={'test_meta_key': 'test_meta_val'}
    interval=10,
    time=1501775008
    values=[3.14]
    ds_name='test_ds_name'
    ds_type='test_ds_type'

class Data(object):

    def __init__(self,
                 host=Constants.host,
                 plugin=Constants.plugin,
                 plugin_instance=Constants.plugin_instance,
                 type=Constants.type,
                 type_instance=Constants.type_instance,
                 meta=Constants.meta,
                 interval=Constants.interval,
                 time=Constants.time,
                 values=Constants.values,
                 ds_name=Constants.ds_name,
                 ds_type=Constants.ds_type):

        self.host = host
        self.plugin = plugin
        self.plugin_instance = plugin_instance
        self.type = type
        self.type_instance = type_instance
        self.meta = meta
        self.interval = interval
        self.time = time
        self.values = values
        self.ds_name = ds_name
        self.ds_type = ds_type

    @staticmethod
    def default_metric():
        return 'host=%s plugin=%s plugin_instance=%s type=%s type_instance=%s ds_name=%s ' \
               'ds_type=%s  test_meta_key=%s %f %d' % (Constants.host, Constants.plugin,
                                                       Constants.plugin_instance,
                                                       Constants.type, Constants.type_instance,
                                                       Constants.ds_name, Constants.ds_type,
                                                       Constants.meta['test_meta_key'],
                                                       Constants.values[0], Constants.time)
