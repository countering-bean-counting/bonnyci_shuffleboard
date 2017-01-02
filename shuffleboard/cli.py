# -*- coding: utf-8 -*-

import click
import requests

import github_api
import shuffleboard as sb


@click.command()
def main(args=None):

    # TODO file path should be an env var and/or arg
    path = '/home/auggy/dev/BonnyCI/shuffleboard_data'

    # TODO set the writer instance type based on command line args

    # dump full response to a file in case something fails in the processing
    # cli_writer = sb.EventsCLIWriter(printer=print)

    csv_writer = sb.EventsCSVWriter(path)
    writer = csv_writer

    header_writer = sb.GhHeaderTxtFileWriter(out_path=path,
                                             filename='gh_headers')

    gh = github_api.GithubGrabber(http_client=requests)
    events = gh.get_events()
    header_writer.write(gh.headers)
    writer.write(events)


if __name__ == "__main__":
    main()
