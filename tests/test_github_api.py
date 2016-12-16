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

# from github3 import GitHub

from shuffleboard import github_api


class MockGithubClient:
    def __init__(self):
        self.issue_populated = type('obj', (object,), {
            "comments_count": 1,
            "body": "issue body",
            "closed_at": "2016-12-15",
            "created_at": "2016-12-15",
            "number": 42,
            "state": "open",
            "updated_at": "2016-12-15",
            "assignee": type('obj', (object,), {"login": "foobear"}),
            "closed_by": type('obj', (object,), {"login": "foobear"}),
            "milestone": type('obj', (object,), {"title": "do it!"}),
            "pull_request": type('obj', (object,), {"number": 1}),
            "user": type('obj', (object,), {"login": "foobear"}),
        })

        self.issue_minimal = type('obj', (object,), {
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
            "user": type('obj', (object,), {"login": "foobear"}),
        })


class TestGithubGrabber(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility function to list the attributes in an object
    # TODO remove this if it ends up not being used
    def _list_fields(self, o):
        fields = []
        for a in filter(lambda a: not a.startswith('__'), dir(o)):
            fields.append(a)
        return fields

    def _issues_on(self, mock_data):
        with patch('github3.GitHub') as mock:
            gh_fake = mock.return_value
            gh_fake.issues_on.return_value = mock_data
            return gh_fake

    def test_extract_attrs(self):
        pass

    def test_get_issues_one(self):
        gh_fake = self._issues_on([MockGithubClient().issue_populated])
        grabber = github_api.GithubGrabber(gh=gh_fake, repo="foo")
        issues = grabber.get_issues()
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

        attributes = expected.keys()
        for a in attributes:
            # check that we didn't drop any fields
            assert hasattr(test_issue, a)
            # check that the values we expected got set
            assert expected[a] == getattr(test_issue, a)

    def test_get_issues_populated(self):
        gh_fake = self._issues_on([MockGithubClient().issue_populated]*3)
        grabber = github_api.GithubGrabber(gh=gh_fake, repo="foo")
        issues = grabber.get_issues()
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

        attributes = expected.keys()
        for a in attributes:
            # check that we didn't drop any fields
            assert hasattr(test_issue, a)
            # check that the values we expected got set
            assert expected[a] == getattr(test_issue, a)

    def test_get_issues_minimal(self):
        gh_fake = self._issues_on([MockGithubClient().issue_minimal]*3)
        grabber = github_api.GithubGrabber(gh=gh_fake, repo="foo")
        issues = grabber.get_issues()
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

        attributes = expected.keys()
        for a in attributes:
            # check that we didn't drop any fields
            assert hasattr(test_issue, a)
            # check that the values we expected got set
            assert expected[a] == getattr(test_issue, a)



    def test_get_issues_empty_set(self):
        gh_fake = self._issues_on([])
        grabber = github_api.GithubGrabber(gh=gh_fake, repo="foo")
        issues = grabber.get_issues()
        assert issues == []



if __name__ == '__main__':
    unittest.main()
