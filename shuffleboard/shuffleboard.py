# -*- coding: utf-8 -*-

import abc
import csv
import os


# abstract class to define an interface for different outputs
class Writer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def write(self, function):
        function()
        return


class CLIWriter(Writer):

    def __init__(self, printer=None):
        self.printer = printer

    def write(self, *args, **kwargs):
        self.printer(*args, **kwargs)
        return


class CSVWriter(Writer):

    def __init__(self, output_path):
        self.output_path = output_path
        # TODO: check output path exists

    def write(self, filename=None, data=[]):
        path = os.path.join(self.output_path, filename)
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=" || ", quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
            for i in data:
                writer.writerow(i)
        return


class DBWriter(Writer):
    # TODO implement DB writes
    def __init__(self):
        pass


class EventsCLIWriter(CLIWriter):

    def __init__(self, printer):
        super().__init__(printer)

    def write(self, events):
        for k, v in events.items():
            self.printer(k)
            if isinstance(v, dict):
                self.printer(v.items())
            else:
                self.printer(v)


class EventsCSVWriter(CSVWriter):

    def __init__(self, output_path):
        super().__init__(output_path)

    def write(self, events):
        # TODO: set filename as current datetimestamp
        filename_prefix = 'test_'
        sheets = self.build_event_rows(events)

        for (name, rows) in sheets.items():
            super().write(filename=filename_prefix + name, data=rows)
        return

    def build_event_rows(self, events):
        sheets = {}
        # split data into sheets
        for (name, event_list) in events.items():
            header_row = []
            rows = []

            # build the header row
            for (k, v) in event_list[0].items():
                header_title = k
                if isinstance(v, dict):
                    titles = list(
                        map(lambda x: '_'.join([header_title, x]), v.keys()))
                    header_row += titles
                else:
                    header_row.append(k)

            rows.append(header_row)

            # build a row for the event data
            # TODO: this is pretty ugly and could be cleaned up
            for e in event_list:
                # set up the csv row
                row = []

                # events are a dict
                for (key, value) in e.items():
                    # the gh response has a series of keys plus a payload dict
                    # so we need to treat the payload dict differently
                    if isinstance(value, dict):
                        # we don't need the full object for certain objects in
                        # the response so just grab the identifier
                        for (k, v) in value.items():
                            if isinstance(v, dict):
                                if 'number' in v:
                                    row.append(v['number'])
                                elif 'login' in v:
                                    row.append(v['login'])
                                elif 'id' in v:
                                    row.append(v['id'])
                                else:
                                    # see if there's something else we
                                    # care about
                                    row.append("Found key %k with value type "
                                               "%v" % (k, type(v)))
                            else:
                                row.append(v)
                    else:
                        row.append(value)

                rows.append(row)

            sheets[name] = rows

        return sheets


class EventsDBWriter(DBWriter):
    # TODO implement db writes for events
    def __init__(self):
        pass

    def write(self, function):
        function()
        return
