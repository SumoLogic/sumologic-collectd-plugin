class Data(object):

    def __init__(self, host=None, plugin=None, plugin_instance=None, type=None, type_instance=None,
                 meta=None, interval=None, time=None, values=None):

        self.host = host
        self.plugin = plugin
        self.plugin_instance = plugin_instance,
        self.type = type
        self.type_instance = type_instance
        self.meta = meta
        self.interval = interval
        self.time = time
        self.values = values
        #self.dstypes = dstypes