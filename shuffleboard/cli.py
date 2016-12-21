# -*- coding: utf-8 -*-

import click
import requests

import github_api

repos = ['shuffleboard']


@click.command()
def main(args=None):

    gh = github_api.GithubGrabber(http_client=requests)

    events = gh.get_events()
    for (repo, typed_events) in events.items():
        print(repo)
        for (typed_event_name, event_list) in typed_events.items():
            print(typed_event_name)
            [print(list(e.items())) for e in event_list]


if __name__ == "__main__":
    main()
