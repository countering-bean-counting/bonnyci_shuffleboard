# -*- coding: utf-8 -*-

import click
from shutil import copyfile
import json
import os
import requests

import github_api
import shuffleboard as sb


@click.command()
def main(args=None):

    # TODO these should be command line args
    path = '/home/auggy/dev/BonnyCI/shuffleboard_data'  # TODO env var option
    use_etag = False
    read_from_file = True
    read_from_file_name = 'events.json'

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

    if read_from_file:
        # read in json file
        events_file = os.path.join(path, read_from_file_name)
        print("reading events from file %s" % events_file)
        with open(events_file, 'r') as f:
            events_json = json.load(f)

        gh = github_api.GithubGrabber()

    else:
        gh = github_api.GithubGrabber(http_client=requests)

        events_args = {}
        if use_etag:
            events_args['etag'] = etag

        events_json = gh.get_events(**events_args)
        header_writer.write(gh.headers)

        # dump json response to file in case something fails
        events_file = os.path.join(path, 'events.json')
        print("dumping events to file %s" % events_file)
        with open(events_file, 'w') as f:
            json.dump(events_json, f)

    if 'no_events' in events_json:
        print("No events received %s" % events_json.values())
    else:
        events = gh.aggregate_events(events_json)
        print("Found new events, writing to %s" % path)
        writer.write(events)
        copyfile(events_file, os.path.join(writer.output_path, 'events.json'))


if __name__ == "__main__":
    main()
