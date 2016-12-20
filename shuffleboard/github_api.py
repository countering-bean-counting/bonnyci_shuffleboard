# -*- coding: utf-8 -*-

import re
import warnings


# Data types for use within Shuffleboard
# TODO these should be explicitly listed out


class Event:
    def __init__(self, attributes):
        for (key, value) in attributes.items():
            setattr(self, key, value)


class IssueEvent(Event):
    def __init__(self, attributes):
        super().__init__(attributes)
        self.action = attributes['action']


class Issue:
    def __init__(self, attributes):
        for (key, value) in attributes.items():
            setattr(self, key, value)

# TODO Milestone

# TODO PullRequest

# TODO Contributor


# Dispatchers to manage data transformation between Github and Shuffleboard

class EventDispatch:
    def __init__(self):
        self.dispatcher = {
            "id": lambda x: x,
            "type": lambda x: x,
            "actor": lambda x: x['login'] if x and 'login' in x else None,
            "repo": lambda x: x['name'] if x and 'name' in x else None,
            "created_at": lambda x: x,
        }


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


# Class to handle getting Github data at the repository level

class GithubGrabber:
    def __init__(self,
                 repos=[],
                 dispatchers=None,
                 owner='BonnyCI',
                 http_client=None,
                 gh_api_base='https://api.github.com'):

        self.owner = owner
        self.repos = repos
        self.gh_api_base = gh_api_base

        self.http_client = http_client

        if dispatchers is None:
            self.dispatchers = self._build_dispatchers()
        else:
            self.dispatchers = dispatchers

    def _build_dispatchers(self):
        return {
            "issue": IssueDispatch().dispatcher,
            "event": EventDispatch().dispatcher,
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

    def get_issues(self):
        issues = {}
        for repo in self.repos:
            repo_endpoint = '/repos/%s/%s/issues' % (self.owner, repo)
            issues_decoded = self._get(self.gh_api_base + repo_endpoint +
                                       '?per_page=100')

            if repo not in issues:
                issues[repo] = []

            for i in issues_decoded:
                issue = Issue(self.extract_fields('issue', i))
                issues[repo].append(issue)
        return issues

    def get_events(self):
        events_endpoint = '/users/%s/events' % (self.owner)
        events_decoded = self._get(self.gh_api_base + events_endpoint +
                                   '?per_page=100')
        events = {}
        for e in events_decoded:
            attributes = self.extract_fields('event', e)

            if re.match("Issue", e['type']):
                attributes['action'] = e['payload']['action']
                attributes['issue'] = e['payload']['issue']['number']
                attributes['instance'] = Issue(self.extract_fields(
                    'issue', e['payload']['issue']))
                event = IssueEvent(attributes)
            else:
                # it's an event type we haven't account for yet
                #  get the payload fields so we can stub it out
                attributes['payload'] = list(e['payload'].keys())
                event = Event(attributes)

            if event.repo not in events:
                events[event.repo] = {}

            if event.type not in events[event.repo]:
                events[event.repo][event.type] = [event]
            else:
                events[event.repo][event.type].append(event)

        return events

