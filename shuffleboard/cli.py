# -*- coding: utf-8 -*-

import click
import requests

import github_api
import shuffleboard as sb


@click.command()
def main(args=None):

    # TODO set the writer instance type based on command line args
    cli_writer = sb.EventsCLIWriter()
    # csv_writer = sb.EventsCSVWriter('/home/auggy/')

    writer = cli_writer

    gh = github_api.GithubGrabber(http_client=requests)
    events = gh.get_events()
    writer.write(events)


if __name__ == "__main__":
    main()
