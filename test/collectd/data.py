class Data(object):

    def __init__(self, host="test_host", plugin="test_plugin",
                 plugin_instance="test_plugin_instance",
                 type="test_type", type_instance="test_type_instance",
                 meta=None, interval=10, time=1501775008, values=3.14,
                 ds_name="test_ds_name", ds_type="test_ds_type"):

        self.host = host
        self.plugin = plugin
        self.plugin_instance = plugin_instance,
        self.type = type
        self.type_instance = type_instance
        self.meta = meta
        self.interval = interval
        self.time = time
        self.values = values
        self.ds_name = ds_name
        self.ds_type = ds_type
