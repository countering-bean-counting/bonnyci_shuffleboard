#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_github_api
----------------------------------

Tests for `github_api` module.
"""


# import sys
import unittest
from unittest.mock import patch
import warnings

# from github3 import GitHub

from shuffleboard import github_api


class MockGithubClient:
    def __init__(self, key=42, repo="repo"):
        self.event = {
            "id": key,
            "type": "Caturday",
            "actor": {"login": "foobear"},
            "repo": {"name": repo},
            "created_at": '2016-12-15',
            "payload": {"cha":"ching"}
        }


class TestGithubGrabber(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get(self, mock_data):
        with patch('requests.Request') as mock:
            http_fake = mock.return_value
            http_fake.get.return_value = type('obj', (object,),
                                              {"json": lambda: mock_data,
                                               "headers": {}})
            return http_fake

    def test_get_events(self):
        expected = MockGithubClient().event
        http_fake = self._get([expected])
        grabber = github_api.GithubGrabber(http_client=http_fake)
        events = grabber.get_events()

        # check that our return structure is keyed on event type
        self.assertTrue('Caturday' in events,
                        msg="%s not in events data" % expected['type'])
        self.assertEqual(len(events['Caturday']), 1)

        got = events['Caturday'][0]

        for e in expected:
            # check that we didn't drop any fields
            self.assertTrue(e in got, msg="missing %s" % e)
            # check that the values we expected got set
            self.assertEqual(expected[e], got[e], msg= "%s value "
                             "didn't match: expected %s, got %s" %
                            (e, expected[e], got[e]))

        # check that we didn't pick up any extra values
        self.assertEqual(sorted(expected.keys()), sorted(got.keys()), msg="found extra values")

if __name__ == '__main__':
    unittest.main()
