# -*- coding: utf-8 -*-

class Constants:
    host = 'test_host'
    plugin = 'test_plugin'
    plugin_instance = 'test_plugin_instance'
    type = 'test_type'
    type_instance = 'test_type_instance'
    meta = {'test_meta_key': 'test_meta_val'}
    interval = 10,
    time = 1501775008
    values = [3.14]
    ds_names = ['test_ds_name']
    ds_types = ['test_ds_type']


class Values:

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
                 ds_names=Constants.ds_names,
                 ds_types=Constants.ds_types):

        self.host = host
        self.plugin = plugin
        self.plugin_instance = plugin_instance
        self.type = type
        self.type_instance = type_instance
        self.meta = meta
        self.interval = interval
        self.time = time
        self.values = values
        self.ds_names = ds_names
        self.ds_types = ds_types

    def metrics_str(self, sep='.'):
        """
        Builds metric string. If sep is not None,
        it includes metric dimension using sep as separator
        """
        metrics = []
        i = 0
        if sep is None:
            metric = ''
        else:
            metric = ' metric=%s' %(sep.join(v for v in (self.type, self.type_instance) if v))

        for (ds_name, ds_type) in zip(self.ds_names, self.ds_types):
            if not self.meta:
                metrics.append('host=%s plugin=%s plugin_instance=%s type=%s type_instance=%s '
                               'ds_name=%s ds_type=%s%s  %f %d' %
                               (self.host, self.plugin, self.plugin_instance, self.type, self.type_instance,
                                ds_name, ds_type, metric, self.values[i], self.time))
            else:
                metrics.append('host=%s plugin=%s plugin_instance=%s type=%s type_instance=%s '
                               'ds_name=%s ds_type=%s%s  test_meta_key=%s %f %d' %
                               (self.host, self.plugin, self.plugin_instance, self.type, self.type_instance,
                                ds_name, ds_type, metric, self.meta['test_meta_key'], self.values[i], self.time))
            i += 1
        return metrics
