# -*- coding: utf-8 -*-
import abc


# abstract class to define an interface for different outputs
class Writer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def write(self, *args, **kwargs): return


class CLIWriter(Writer):

    def __init__(self, printer=None):
        self.printer = printer

    def write(self, *args, **kwargs):
        self.printer(*args, **kwargs)
