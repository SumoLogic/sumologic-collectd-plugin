# -*- coding: utf-8 -*-

class CollectdConfig:
    def __init__(self, children):
        self.children = children

    def children(self):
        return self.children

class ConfigNode:
    def __init__(self, key, values):
        self.key = key
        self.values = values

    def key(self):
        return self.key

    def values(self):
        return self.values
