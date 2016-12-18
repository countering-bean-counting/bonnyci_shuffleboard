# -*- coding: utf-8 -*-

import click
import requests

import github_api

repos = ['shuffleboard']


@click.command()
def main(args=None):

    gh = github_api.GithubGrabber(repos=repos, http_client=requests)

    issues = gh.get_issues()
    for (repo, issues_list) in issues.items():
        print("repo")
        [print(vars(i)) for i in issues_list]

    events = gh.get_events()
    for (repo, typed_events) in events.items():
        print(repo)
        for (typed_event_name, event_list) in typed_events.items():
            print(typed_event_name)
            [print (vars(e)) for e in event_list]

if __name__ == "__main__":
    main()
