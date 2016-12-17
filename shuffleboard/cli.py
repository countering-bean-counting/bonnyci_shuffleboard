# -*- coding: utf-8 -*-

import click
import requests

import github_api

repos = ['shuffleboard']


@click.command()
def main(args=None):

    for repo in repos:
        gh = github_api.GithubGrabber(repo=repo, http_client=requests)
        issues = gh.get_issues_for_repo()

        for i in issues:
            print(vars(i))

        issue_events = gh.get_issue_events_for_repo()

        for i in issue_events:
            print(vars(i))


if __name__ == "__main__":
    main()
