# -*- coding: utf-8 -*-

import click
import requests
import pprint

import github_api
import plunder
import shuffleboard


@click.command()
def main(args=None):

    # TODO set this instance type based on command line args
    writer = shuffleboard.EventsCLIWriter()

    gh = github_api.GithubGrabber(http_client=requests)
    events = gh.get_events()
    writer.write(events)


if __name__ == "__main__":
    main()
