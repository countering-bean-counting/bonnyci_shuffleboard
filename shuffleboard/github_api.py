# -*- coding: utf-8 -*-

from github3 import GitHub


def get_github_issues_for_repo(repo):
    gh = GitHub()

    issues_raw = gh.issues_on(username='BonnyCI', repository=repo)

    field_mapper = {
        "comments_count": lambda x: x.comments_count,
        "body": lambda x: x.body,
        "closed_at": lambda x: x.closed_at,
        "created_at": lambda x: x.created_at,
        "number": lambda x: x.number,
        "state": lambda x: x.state,
        "updated_at": lambda x: x.updated_at,
        "assignee":
            lambda x: x.assignee.login if hasattr(x.assignee, 'login') else
            None,
        "closed_by":
            lambda x: x.closed_by.login if hasattr(x.closed_by, 'login')
            else None,
        "milestone":
            lambda x: x.milestone.title if hasattr(x.milestone, 'title')
            else None,
        "pull_request": lambda x: x.pull_request.number if hasattr(
            x.pull_request, 'number') else None,
        "user": lambda x: x.user.login if hasattr(x.user, 'login') else None
    }

    issues = []
    for i in issues_raw:
        attributes = {}

        for a in filter(
         lambda a: not a.startswith('__') and a in field_mapper, dir(i)):
            attributes[a] = field_mapper[a](i)

        issue = Issue(attributes)
        issues.append(issue)

    return issues


class Issue:
    def __init__(self, attributes):
        for (key, value) in attributes.items():
            setattr(self, key, value)
