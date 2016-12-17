# -*- coding: utf-8 -*-

import warnings


# Data types for use within Shuffleboard

class Issue:
    def __init__(self, attributes):
        for (key, value) in attributes.items():
            setattr(self, key, value)


class IssueEvent:
    def __init__(self, attributes):
        for (key, value) in attributes.items():
            setattr(self, key, value)


class IssueCommentEvent:  # TODO
    def __init__(self, attributes):
        for (key, value) in attributes.items():
            setattr(self, key, value)


# Dispatchers to manage data transformation between Github and Shuffleboard

class IssueDispatch:
    def __init__(self):
        self.dispatcher = {
            "comments_count": lambda x: x,
            "body": lambda x: x,
            "closed_at": lambda x: x,
            "created_at": lambda x: x,
            "number": lambda x: x,
            "state": lambda x: x,
            "updated_at": lambda x: x,
            "assignee": lambda x: x['login'] if x and 'login' in x else None,
            "closed_by": lambda x: x['login'] if x and 'login' in x else None,
            "milestone": lambda x: x['title'] if x and 'title' in x else None,
            "pull_request": lambda x: x['number'] if x and 'number' in x
            else None,
            "user": lambda x: x['login'] if x and 'login' in x else None
        }


class IssueEventDispatch:
    def __init__(self):
        self.dispatcher = {
            "id": lambda x: x,
            "event": lambda x: x,
            "created_at": lambda x: x,
            "actor": lambda x: x['login'] if x and 'login' in x else None,
            "issue": lambda x: x['number'] if x and 'number' in x else None,
            "commit_id": lambda x: x,
            "commit_url": lambda x: x
        }


class IssueCommentEventDispatch:
    def __init__(self):
        self.dispatcher = {
            # TODO
        }


# Class to handle getting Github data at the repository level

class GithubGrabber:
    def __init__(self,
                 repo='',
                 dispatchers=None,
                 owner='BonnyCI',
                 http_client=None,
                 gh_api_base='https://api.github.com'):

        self.owner = owner
        self.repo = repo
        self.gh_api_base = gh_api_base

        self.http_client = http_client

        if dispatchers is None:
            self.dispatchers = self._build_dispatchers()
        else:
            self.dispatchers = dispatchers

    def _build_dispatchers(self):
        return {
            "issue": IssueDispatch().dispatcher,
            "issue_event": IssueEventDispatch().dispatcher,
            "issue_comment_event": IssueCommentEventDispatch().dispatcher
        }

    def _get(self, url):
        response = self.http_client.get(url)
        return response.json()

    def extract_fields(self, dispatcher_type, data):
        if dispatcher_type in self.dispatchers:
            dispatcher = self.dispatchers[dispatcher_type]
        else:
            warnings.warn("dispatcher_type %s not found" % dispatcher_type)
            return []

        attributes = {}
        for a in filter(lambda a: a in dispatcher, data.keys()):
            attributes[a] = dispatcher[a](data[a])
        return attributes

    def get_issues_for_repo(self, repo_endpoint=None):

        if not self.repo:
            warnings.warn("Can't get_issues_for_repo without a repo!")
            return []

        if not repo_endpoint:
            repo_endpoint = '/repos/%s/%s/issues' % (self.owner, self.repo)

        issues_decoded = self._get(self.gh_api_base + repo_endpoint)

        issues = {}
        for i in issues_decoded:
            issue = Issue(self.extract_fields('issue', i))
            issues[issue.number] = issue
        return issues

    def get_issue_events_for_repo(self, repo_endpoint=None):
        if not self.repo:
            warnings.warn("Can't get_issue_events_for_repo without a repo!")
            return []

        if not repo_endpoint:
            repo_endpoint = '/repos/%s/%s/issues/events' % (self.owner,
                                                            self.repo)

        issue_events_decoded = self._get(self.gh_api_base + repo_endpoint)

        issue_events = {}
        for i in issue_events_decoded:
            issue_event = IssueEvent(self.extract_fields('issue_event', i))
            if issue_event.issue in issue_events:
                issue_events[issue_event.issue].append(issue_event)
            else:
                issue_events[issue_event.issue] = [issue_event]
        return issue_events

    def get_issues_comment_events(self):
        return
