# -*- coding: utf-8 -*-

import abc
import base64
import csv
import collections
import datetime as dt
import json
import os

# TODO: this should be more composable

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

    def __init__(self, csv_writer=csv.writer):
        self.csv_writer = csv_writer

    def write(self, file=None, data=[]):
        with open(file, 'w', newline='') as csvfile:
            writer = self.csv_writer(csvfile, delimiter=',',
                                     quotechar='"', quoting=csv.QUOTE_ALL)
            for i in data:
                writer.writerow(i)
        return

    def build_rows(self, data=[]):
        header_row = sorted(list(data[0].keys()))

        data_rows = []
        sheet = []
        for row in data:
            # Github is inconsistent which screws up the data
            ordered_row = collections.OrderedDict(sorted(row.items()))

            # missing keys get a null value
            for k in header_row:
                if k not in ordered_row.keys():
                    ordered_row[k] = None
                    ordered_row = \
                        collections.OrderedDict(sorted(ordered_row.items()))

            # handle extra keys
            for k in row.keys():
                if k not in header_row:
                    header_row.append(k)
                    header_row = sorted(header_row)
                    # get the position for the new key
                    i = header_row.index(k)
                    # update the rows we've already processed
                    for r in data_rows:
                        r.insert(i, None)
            data_rows.append(list(ordered_row.values()))

        sheet.append(header_row)
        sheet += data_rows
        return sheet


# TODO remove out_path, all that should be in the file arg
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


# TODO remove out_path, all of that should just be in the file arg
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

    def __init__(self, *args, **kwargs):
        self.timestamp = dt.datetime.utcnow().strftime("%Y%m%d_%H%M")
        super().__init__(*args, **kwargs)

    def write(self, out_path=None, events=[]):
        filename_prefix = 'events_'
        sheets = self.build_rows(events)

        events_out_path = os.path.join(out_path, 'events_' + self.timestamp)
        os.makedirs(events_out_path)

        for (event_name, rows) in sheets.items():
            filename = filename_prefix + event_name + '.csv'
            super().write(file=os.path.join(events_out_path, filename),
                          data=rows)
        return

    def build_rows(self, events):

        event_type_header_row_dispatch = {
            'CreateEvent': None,
            'DeleteEvent': None,
            'ForkEvent': None,
            'GollumEvent': 'payload_pages_page_name',
            'IssueCommentEvent': 'payload_issue_number',
            'IssuesEvent': 'payload_issue_number',
            'MemberEvent': None,
            'PullRequestEvent': 'payload_pull_request_number',
            'PullRequestReviewCommentEvent': 'payload_pull_request_number',
            'PushEvent': None,
            'WatchEvent': None
        }

        event_type_data_row_dispatch = {
            'CreateEvent': lambda x: None,
            'DeleteEvent': lambda x: None,
            'ForkEvent': lambda x: None,
            'GollumEvent':
                lambda x: x['payload']['pages'][0]['page_name'],
            'IssueCommentEvent':
                lambda x: x['payload']['issue']['number'],
            'IssuesEvent':
                lambda x: x['payload']['issue']['number'],
            'MemberEvent': lambda x: None,
            'PullRequestEvent':
                lambda x: x['payload']['pull_request']['number'],
            'PullRequestReviewCommentEvent':
                lambda x: x['payload']['pull_request']['number'],
            'PushEvent': lambda x: None,
            'WatchEvent': lambda x: None
        }

        sheets = {}
        extra = None
        # split data into sheets
        for (event_name, event_list) in events.items():
            header_row = []
            data_rows = []
            sheets[event_name] = []

            # build the header row
            for (k, v) in event_list[0].items():
                header_title = k

                if header_title == 'payload' and isinstance(v, str):
                        v = json.loads(v)

                if isinstance(v, dict):
                    titles = list(
                        map(lambda x: '_'.join([header_title, x]), v.keys()))
                    header_row += titles
                else:
                    header_row.append(k)

            extra_key = event_type_header_row_dispatch[event_name]
            if extra_key:
                header_row.append(extra_key)
                sorted_header = sorted(header_row)
                extra = sorted_header.index(extra_key)
                sheets[event_name].append(sorted_header)
            else:
                sheets[event_name].append(sorted(header_row))

            # build a row for the event data
            # TODO: this is pretty ugly and could be cleaned up
            for e in event_list:
                # set up the csv row
                row = []

                if isinstance(e['payload'], str):
                    decoded = json.loads(e['payload'])
                    e['payload'] = dict(decoded.items())

                # events are a dict
                for (key, value) in sorted(e.items()):
                    # the gh response has a series of keys plus a payload
                    # object with keys that vary by event type
                    if isinstance(value, dict):
                        for (k, v) in sorted(value.items()):
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
                extra_value = event_type_data_row_dispatch[event_name](e)
                if extra_value:
                    row.insert(extra, extra_value)
                data_rows.append(row)

            sheets[event_name] += data_rows

        return sheets

    def aggregate_events(self, events):
        events_aggregated = {}

        for e in events:
            event_type = e['type']

            if event_type not in events_aggregated:
                events_aggregated[event_type] = [e]
            else:
                events_aggregated[event_type].append(e)

        return events_aggregated


class EventsTxtFileWriter(TxtFileWriter):
    # TODO dump response to a text file in case of parsing issues
    def __init__(self):
        pass


class EventsDBWriter(DBWriter):
    # TODO implement db writes for events
    def __init__(self):
        pass


# repos with an org have an extra "organization" column
class RepoDataCSVWriter(CSVWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra_fields = [
            "organization",
            "parent",
            "source",
            "is_deleted", # custom fields added for manually fetched repo data
            "last_event_at",
            "last_event_type",
            "create_event_type"
        ]

    def build_rows(self, data={}):
        for field in self.extra_fields:
            if field not in data.keys():
                data[field] = ""

        ordered_data = sorted(data.items())
        header_row = list(i[0] for i in ordered_data)
        data_row = list(i[1] for i in ordered_data)
        sheet = [header_row, data_row]
        return sheet


class DictCSVWriter(CSVWriter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_rows(self, data={}):
        ordered_data = sorted(data.items())
        header_row = list(i[0] for i in ordered_data)
        data_row = list(i[1] for i in ordered_data)
        sheet = [header_row, data_row]
        return sheet


# JSON obj where the key is a data column
class KeyAsColumnDictCSVWriter(CSVWriter):

    def __init__(self, header_row=[], *args, **kwargs):
        self.header_row = header_row
        super().__init__(*args, **kwargs)

    def build_rows(self, data={}):
        ordered_data = sorted(data.items())

        data_rows = []
        sheet = []

        for k, v in ordered_data:
            data_rows.append([k, v])

        sheet.append(self.header_row)
        sheet += data_rows
        return sheet


# JSON obj where columns contain JSON objects
class ListOfDictsCSVWriter(CSVWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_rows(self, data=[]):
        sheet = []

        # build the header row
        header_row = []
        for (key, value) in sorted(data[0].items()):
            header_title = key

            if isinstance(value, dict):
                titles = list(
                    map(lambda x: '_'.join([header_title, x]), value.keys()))
                header_row += titles
            else:
                header_row.append(key)

        sheet.append(sorted(header_row))

        # build the data rows
        data_rows = []
        for i in data:
            row = []
            for (key, value) in sorted(i.items()):
                # extract dictionary items
                if isinstance(value, dict):
                    for (k, v) in sorted(value.items()):
                        if isinstance(v, dict):
                            row.append(json.dumps(dict(sorted(v.items()))))
                        else:
                            row.append(v)
                else:
                    row.append(value)

            data_rows.append(row)

        sheet += data_rows
        return sheet


class Base64DictCSVWriter(CSVWriter):

    def __init__(self, fields=[], *args, **kwargs):

        # {field:type}
        self.fields = fields

        super().__init__(*args, **kwargs)

    def build_rows(self, data={}):
        header_row = list(data.keys())

        for field in self.fields:
            data[field] = str(base64.b64decode(data[field]))

        data_row = list(data.values())

        sheet = [header_row, data_row]
        return sheet


writer_lookup = {
    'repo_languages': KeyAsColumnDictCSVWriter(header_row=['language', 'loc']),
    'repo_owner': DictCSVWriter(),
    'repo_data': RepoDataCSVWriter(),
    'repo_contributors': ListOfDictsCSVWriter(),
    'repo_readme': Base64DictCSVWriter(fields=['content']),
    'yml_travis': Base64DictCSVWriter(fields=['content']),
    'yml_circleci': Base64DictCSVWriter(fields=['content']),
    'yml_appveyor': Base64DictCSVWriter(fields=['content']),
    'repo_pulls': ListOfDictsCSVWriter(),
    'statuses': ListOfDictsCSVWriter()
}
