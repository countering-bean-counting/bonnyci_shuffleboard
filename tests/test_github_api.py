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
    def __init__(self):
        self.issue_populated = {
            "comments_count": 1,
            "body": "issue body",
            "closed_at": "2016-12-15",
            "created_at": "2016-12-15",
            "number": 42,
            "state": "open",
            "updated_at": "2016-12-15",
            "assignee": {"login": "foobear"},
            "closed_by": {"login": "foobear"},
            "milestone": {"title": "do it!"},
            "pull_request": {"number": 1},
            "user": {"login": "foobear"},
            "extra1": "HELO",
            "extra2": "ACK"
        }

        self.issue_minimal = {
            "comments_count": None,
            "body": None,
            "closed_at": None,
            "created_at": "2016-12-15",
            "number": 42,
            "state": "open",
            "updated_at": "2016-12-15",
            "assignee": None,
            "closed_by": None,
            "milestone": None,
            "pull_request": None,
            "user": {"login": "foobear"},
            "extra1": None,
            "extra2": None
        }


class TestGithubGrabber(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility function to list the attributes in an object
    def _list_attributes(self, o):
        attributes = []
        for a in filter(lambda a: not a.startswith('__'), dir(o)):
            attributes.append(a)
        return sorted(attributes)

    def _get(self, mock_data):
        with patch('requests.Request') as mock:
            http_fake = mock.return_value
            http_fake.get.return_value = type('obj', (object,),
                                              {"json": lambda: mock_data})
            return http_fake

    def test_extract_attrs(self):
        # create a GithubGrabber instance with a custom test dispatcher
        fake_dispatcher = {"bar": lambda x: x}
        gh = github_api.GithubGrabber(dispatchers={
                                          "fake_dispatcher": fake_dispatcher},
                                      http_client=None)
        result = gh.extract_fields(dispatcher_type="fake_dispatcher",
                                   data={"bar": "baz"})

        assert result == {"bar": "baz"}

    def test_extract_attrs_bad_dispatcher_type(self):

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")

            # create a GithubGrabber instance with no dispatchers
            gh = github_api.GithubGrabber(dispatchers={}, http_client=None)
            result = gh.extract_fields(dispatcher_type="bad", data=None)
            # check that we get the expected empty list back
            assert result == []

            # Check that a warning was issued
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "dispatcher_type" in str(w[-1].message)

    def test_get_issues_one(self):
        http_fake = self._get([MockGithubClient().issue_populated])
        grabber = github_api.GithubGrabber(http_client=http_fake, repo="foo")
        issues = grabber.get_issues_for_repo()
        test_issue = issues[0]

        expected = {
            "comments_count": 1,
            "body": "issue body",
            "closed_at": "2016-12-15",
            "created_at": "2016-12-15",
            "number": 42,
            "state": "open",
            "updated_at": "2016-12-15",
            "assignee": "foobear",
            "closed_by": "foobear",
            "milestone": "do it!",
            "pull_request": 1,
            "user": "foobear"
        }

        expected_attr = sorted(expected.keys())
        for a in expected_attr:
            # check that we didn't drop any fields
            assert hasattr(test_issue, a)
            # check that the values we expected got set
            assert expected[a] == getattr(test_issue, a)

        # check that we didn't pick up any extra values
        assert expected_attr == self._list_attributes(test_issue)

    def test_get_issues_populated(self):
        http_fake = self._get([MockGithubClient().issue_populated] * 3)
        grabber = github_api.GithubGrabber(http_client=http_fake, repo="foo")
        issues = grabber.get_issues_for_repo()
        test_issue = issues[0]

        expected = {
            "comments_count": 1,
            "body": "issue body",
            "closed_at": "2016-12-15",
            "created_at": "2016-12-15",
            "number": 42,
            "state": "open",
            "updated_at": "2016-12-15",
            "assignee": "foobear",
            "closed_by": "foobear",
            "milestone": "do it!",
            "pull_request": 1,
            "user": "foobear"
        }

        expected_attr = sorted(expected.keys())
        for a in expected_attr:
            # check that we didn't drop any fields
            assert hasattr(test_issue, a)
            # check that the values we expected got set
            assert expected[a] == getattr(test_issue, a)

        # check that we didn't pick up any extra values
        assert expected_attr == self._list_attributes(test_issue)

    def test_get_issues_minimal(self):
        http_fake = self._get([MockGithubClient().issue_minimal] * 3)
        grabber = github_api.GithubGrabber(http_client=http_fake, repo="foo")
        issues = grabber.get_issues_for_repo()
        test_issue = issues[0]

        expected = {
            "comments_count": None,
            "body": None,
            "closed_at": None,
            "created_at": "2016-12-15",
            "number": 42,
            "state": "open",
            "updated_at": "2016-12-15",
            "assignee": None,
            "closed_by": None,
            "milestone": None,
            "pull_request": None,
            "user": "foobear"
        }

        expected_attr = sorted(expected.keys())
        for a in expected_attr:
            # check that we didn't drop any fields
            assert hasattr(test_issue, a)
            # check that the values we expected got set
            assert expected[a] == getattr(test_issue, a)

        # check that we didn't pick up any extra values
        assert expected_attr == self._list_attributes(test_issue)

    def test_get_issues_empty_set(self):
        http_fake = self._get([])
        grabber = github_api.GithubGrabber(http_client=http_fake, repo="foo")
        issues = grabber.get_issues_for_repo()
        assert issues == []

if __name__ == '__main__':
    unittest.main()
