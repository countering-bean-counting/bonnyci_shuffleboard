# -*- coding: utf-8 -*-

import abc
import csv
import datetime as dt
import json
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

    def __init__(self, output_path, csv_writer=csv.writer):
        self.output_path = output_path
        self.csv_writer = csv_writer
        # TODO: check output path exists

    def write(self, filename=None, data=[]):
        path = os.path.join(self.output_path, filename)
        with open(path, 'w', newline='') as csvfile:
            writer = self.csv_writer(csvfile, delimiter='|',
                                     quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in data:
                writer.writerow(i)
        return

    def combine_rows(self):
        pass

    def combine_json(self):
        pass


class TxtFileWriter(Writer):

    def __init__(self, out_path=None, writer=None, filename=None):
        self.path = os.path.join(out_path, filename)
        self.writer = writer

    def write(self, data=None):
        if self.writer:
            self.writer.write(data)
        else:
            print("writing data to %s" % self.path)
            with open(self.path, 'w') as f:
                f.write(data)


class DBWriter(Writer):
    # TODO implement DB writes
    def __init__(self):
        pass

    def write(self, function):
        super()


class GhHeaderTxtFileWriter(TxtFileWriter):
    def __init__(self, filename=None, out_path=None, writer=None, *args,
                 **kwargs):
        super().__init__(filename=filename, out_path=out_path,
                         writer=writer, *args, *kwargs)

    def write(self, data={}):
        super().write(json.dumps(dict(data)))


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

    def __init__(self, output_path, *args, **kwargs):
        self.timestamp = dt.datetime.utcnow().strftime("%Y%m%d_%H%M")
        output_path = os.path.join(output_path, 'events_' + self.timestamp)
        super().__init__(output_path=output_path, *args, **kwargs)

    def write(self, events):
        filename_prefix = 'events_'
        sheets = self.build_event_rows(events)

        os.makedirs(self.output_path)
        for (event_name, rows) in sheets.items():
            super().write(filename=filename_prefix + event_name + '_' +
                          self.timestamp + '.csv', data=rows)
        return

    def build_event_rows(self, events):

        event_type_header_row_dispatch = {
            'CreateEvent': lambda x: x,
            'DeleteEvent': lambda x: x,
            'ForkEvent': lambda x: x,
            'GollumEvent': lambda x: x.append('payload_pages_page_name'),
            'IssueCommentEvent': lambda x: x.append('payload_issue_number'),
            'IssuesEvent': lambda x: x.append('payload_issue_number'),
            'PullRequestEvent': lambda x: x.append(
                'payload_pull_request_number'),
            'PullRequestReviewCommentEvent': lambda x: x.append(
                'payload_pull_request_number'),
            'PushEvent': lambda x: x,
            'WatchEvent': lambda x: x
        }

        event_type_data_row_dispatch = {
            'CreateEvent': lambda x, y: x,
            'DeleteEvent': lambda x, y: x,
            'ForkEvent': lambda x, y: x,
            'GollumEvent':
                lambda x, y: x.append(y['payload']['pages'][0]['page_name']),
            'IssueCommentEvent':
                lambda x, y: x.append(y['payload']['issue']['number']),
            'IssuesEvent':
                lambda x, y: x.append(y['payload']['issue']['number']),
            'PullRequestEvent':
                lambda x, y: x.append(y['payload']['pull_request']['number']),
            'PullRequestReviewCommentEvent':
                lambda x, y: x.append(y['payload']['pull_request']['number']),
            'PushEvent': lambda x, y: x,
            'WatchEvent': lambda x, y: x
        }

        sheets = {}
        # split data into sheets
        for (event_name, event_list) in events.items():
            header_row = []
            data_rows = []
            sheets[event_name] = []

            # build the header row
            for (k, v) in event_list[0].items():
                header_title = k
                if isinstance(v, dict):
                    titles = list(
                        map(lambda x: '_'.join([header_title, x]), v.keys()))
                    header_row += titles
                else:
                    header_row.append(k)

            event_type_header_row_dispatch[event_name](header_row)
            sheets[event_name].append(header_row)

            # build a row for the event data
            # TODO: this is pretty ugly and could be cleaned up
            for e in event_list:
                # set up the csv row
                row = []

                if isinstance(e['payload'], str):
                    decoded = json.loads(e['payload'])
                    e['payload'] = decoded

                # events are a dict
                for (key, value) in e.items():
                    # the gh response has a series of keys plus a payload
                    # object with keys that vary by event type
                    if isinstance(value, dict):
                        for (k, v) in value.items():
                            if isinstance(v, dict):
                                # serialize any objects contained in the
                                # payload so we don't have to do an api call
                                #  later to get these details
                                row.append(json.dumps(dict(v.items())))
                            else:
                                row.append(v)
                    else:
                        row.append(value)

                # add fields for convenience based on event type
                event_type_data_row_dispatch[event_name](row, e)

                data_rows.append(row)

            sheets[event_name] += data_rows

        return sheets


class EventsTxtFileWriter(TxtFileWriter):
    # TODO dump response to a text file in case of parsing issues
    def __init__(self):
        pass


class EventsDBWriter(DBWriter):
    # TODO implement db writes for events
    def __init__(self):
        pass
