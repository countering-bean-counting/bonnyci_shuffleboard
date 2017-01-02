# -*- coding: utf-8 -*-

import click
import json
import os
import requests

import github_api
import shuffleboard as sb


@click.command()
def main(args=None):

    # TODO file path should be an env var and/or arg
    path = '/home/auggy/dev/BonnyCI/shuffleboard_data'

    header_file = os.path.join(path, 'gh_headers')
    with open(header_file, 'r') as f:
        last_headers = json.load(f)
        etag = last_headers["ETag"][2:]

    # TODO set the writer instance type based on command line args
    # cli_writer = sb.EventsCLIWriter(printer=print)
    csv_writer = sb.EventsCSVWriter(output_path=path)
    writer = csv_writer

    header_writer = sb.GhHeaderTxtFileWriter(out_path=path,
                                             filename='gh_headers')

    gh = github_api.GithubGrabber(http_client=requests)
    events = gh.get_events() #(etag=etag)
    header_writer.write(gh.headers)
    # TODO dump full response to a file in case something fails

    if 'no_events' in events:
        print("No events received %s" % events.values())
    else:
        print("Found new events, writing to %s" % path)
        writer.write(events)


if __name__ == "__main__":
    main()
