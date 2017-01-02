#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_shuffleboard
----------------------------------

Tests for `shuffleboard` module.
"""

import json
import unittest
import re

from shuffleboard import github_api as gha
from shuffleboard import shuffleboard as sb

# setting a global var since I'm not sure how singletons work in Python
#  also this pattern is really sloppy but it does the job for now
MOCK_OUTPUT = {}


# Mock a csv class that overrides our methods so we don't actually write a
# file and can just capture the output
class MockCSVWriter:
    def __init__(self, csvfile=None, *args, **kwargs):
        self.csvfile = csvfile
        MOCK_OUTPUT[csvfile.name] = []
        self.sheet = MOCK_OUTPUT[csvfile.name]

    def writerow(self, i):
        self.sheet.append(i)


class MockTxtFileWriter:
    def __init__(self):
        self.data = None

    def write(self, data):
        self.data = data
        return


class TestShuffleboard(unittest.TestCase):

    def setUp(self):
        # use this to parse json instead of having to maintain separate files
        self.gh = gha.GithubGrabber(http_client=None)

        with open('tests/github_events.json', 'r') as f:
            self.events_json = json.load(f)
            self.events = self.gh.aggregate_events(self.events_json)

        with open('tests/gh_headers.json', 'r') as f:
            self.gh_headers = json.load(f)

    def tearDown(self):
        pass

    def test_events_cli_writer(self):
        output = []
        writer = sb.EventsCLIWriter(printer=output.append)
        writer.write(self.events)
        # print(output) # for debugging
        self.assertEqual(16, len(output))

    def test_events_csv_writer(self):
        csv_writer = MockCSVWriter
        # TODO: this should use mock_open to prevent empty file creation
        writer = sb.EventsCSVWriter(
            '/tmp',
            csv_writer=csv_writer)
        writer.write(self.events)

        # minimal tests to make sure the format is right
        self.assertTrue('/tmp/events_PullRequestEvent' in MOCK_OUTPUT)
        self.assertEqual(len(MOCK_OUTPUT.keys()), 8)
        self.assertTrue(isinstance(MOCK_OUTPUT['/tmp/events_PullRequestEvent'],
                                   list))
        self.assertTrue(isinstance(MOCK_OUTPUT[
                                       '/tmp/events_PullRequestEvent'][0],
                                   list))
        # clear it out in case other tests use it
        #  again, this is not an ideal pattern but it works for now
        MOCK_OUTPUT.clear()

    def test_gh_headers_txt_writer(self):
        # just checks running the code path and documents the expected
        # format for recording the github headers from the last run
        mock_writer = MockTxtFileWriter()
        header_writer = sb.GhHeaderTxtFileWriter(writer=mock_writer,
                                                 filename='foo',
                                                 out_path='foo')
        header_writer.write(self.gh_headers)
        self.assertEqual(len(mock_writer.data), 924)
        self.assertTrue(re.match('{".*"}', mock_writer.data))

if __name__ == '__main__':
    unittest.main()
