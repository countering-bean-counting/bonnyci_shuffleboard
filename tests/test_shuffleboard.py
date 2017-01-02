#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_shuffleboard
----------------------------------

Tests for `shuffleboard` module.
"""


# import sys
import json
from io import StringIO
import unittest
import sys

from shuffleboard import github_api as gha
from shuffleboard import shuffleboard as sb


class TestShuffleboard(unittest.TestCase):

    def setUp(self):
        # use this to parse json instead of having to maintain separate files
        self.gh = gha.GithubGrabber(http_client=None)

        with open('tests/github_events.json', 'r') as f:
            self.events_json = json.load(f)
            self.events = self.gh.aggregate_events(self.events_json)

    def tearDown(self):
        pass

    def test_events_cli_writer(self):
        output = []
        writer = sb.EventsCLIWriter(printer=output.append)
        writer.write(self.events)
        # for debugging
        # print(output)
        self.assertEqual(16, len(output))

    def test_events_csv_writer(self):
        output = []
        writer = sb.EventsCSVWriter(
            '/home/auggy/dev/BonnyCI/shuffleboard_data')
        writer.write(self.events)
        # for debugging
        print(output)
        #self.assertEqual(16, len(output))

if __name__ == '__main__':
    unittest.main()
