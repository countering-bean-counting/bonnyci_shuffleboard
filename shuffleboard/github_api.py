# -*- coding: utf-8 -*-

from github3 import GitHub
import warnings


# Data types for use within Shuffleboard

class Issue:
    def __init__(self, attributes):
        for (key, value) in attributes.items():
            setattr(self, key, value)


class IssueEvents:  # TODO
    def __init__(self, attributes):
        for (key, value) in attributes.items():
            setattr(self, key, value)


class IssueCommentEvents:  # TODO
    def __init__(self, attributes):
        for (key, value) in attributes.items():
            setattr(self, key, value)


# Dispatchers to manage data transformation between Github and Shuffleboard

class IssueDispatch:
    def __init__(self):
        self.dispatcher = {
                "comments_count": lambda x: x.comments_count,
                "body": lambda x: x.body,
                "closed_at": lambda x: x.closed_at,
                "created_at": lambda x: x.created_at,
                "number": lambda x: x.number,
                "state": lambda x: x.state,
                "updated_at": lambda x: x.updated_at,
                "assignee": lambda x: x.assignee.login if hasattr(
                    x.assignee, 'login') else None,
                "closed_by": lambda x: x.closed_by.login if hasattr(
                    x.closed_by, 'login') else None,
                "milestone": lambda x: x.milestone.title if hasattr(
                    x.milestone, 'title') else None,
                "pull_request": lambda x: x.pull_request.number if hasattr(
                    x.pull_request, 'number') else None,
                "user": lambda x: x.user.login if hasattr(x.user, 'login')
                else None
            }


class IssueEventDispatch:
    def __init__(self):
        self.dispatcher = {
            # TODO
        }


class IssueCommentEventDispatch:
    def __init__(self):
        self.dispatcher = {
            # TODO
        }


# Class to handle getting Github data

class GithubGrabber:
    def __init__(self, repo, dispatchers=None, owner='BonnyCI', gh=GitHub()):

        self.gh = gh
        self.repo = repo
        self.owner = owner

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

    def extract_attrs(self, dispatcher_type, obj):
        if dispatcher_type in self.dispatchers:
            dispatcher = self.dispatchers[dispatcher_type]
        else:
            warnings.warn("dispatcher_type %s not found" % dispatcher_type)
            return []

        attributes = {}
        for a in filter(
            lambda a:
                not a.startswith('__') and a in dispatcher, dir(obj)):
            attributes[a] = dispatcher[a](obj)
        return attributes

    def get_issues(self):
        issues_raw = self.gh.issues_on(username=self.owner,
                                       repository=self.repo)

        issues = []
        for i in issues_raw:
            issue = \
                Issue(self.extract_attrs('issue', i))
            issues.append(issue)
        return issues

    def get_issue_events(self):
        return

    def get_issues_comment_events(self):
        return
