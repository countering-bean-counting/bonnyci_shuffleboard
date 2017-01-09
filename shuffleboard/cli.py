# -*- coding: utf-8 -*-

import click
from shutil import copyfile
import glob
import json
import os
import re
import requests

import github_api
import shuffleboard as sb


@click.command()
def main(args=None):

    # TODO these should be command line args
    # project = "BonnyCI"
    path = '/home/auggy/dev/BonnyCI/shuffleboard_data'  # TODO env var option
    use_etag = True
    read_from_file = False
    read_from_file_name = 'events.json'
    first_run_folder = '/home/auggy/dev/BonnyCI/shuffleboard_data/first_run_in'
    first_run = True

    if first_run:

        # get a list of all json files at the top level starting with "event"
        events_list = []
        for events_file in glob.glob(first_run_folder + '/' + 'events*.json'):
            print("reading events file %s", events_file)
            # combine file contents into one json structure
            f = open(events_file, 'r')
            content = f.read()
            if re.match('\[', content):
                parsed_content = json.loads(content)
                events_list += parsed_content
            else:
                parsed_content = ','.join(content.split('}\n{'))
                events_list.append(json.loads(parsed_content))

        gh = github_api.GithubGrabber()
        events = gh.aggregate_events(events_list)
        print("Writing events to %s" % first_run_folder)
        events_writer = sb.EventsCSVWriter(output_path=first_run_folder)
        events_writer.write(events)

        # get a list of all directory names (these should be repo names)
        walk = tuple(os.walk(first_run_folder))
        repos = walk[0][1]

        # for each directory
        for repo in repos:
            repo_folder = os.path.join(first_run_folder, repo)
            csv_writer = sb.CSVWriter(repo_folder)

            entities = ['labels', 'milestones', 'issues']
            # entities = []

            for entity in entities:
                write_entity(entity=entity, repo_folder=repo_folder,
                             writer=csv_writer)

        # don't run the rest of the script
        exit()

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

    if 'no_events' in events_json:
        print("No events received %s" % list(events_json.values()))
    else:
        # dump json response to file in case something fails
        events_file = os.path.join(path, 'events.json')
        print("dumping events to file %s" % events_file)
        with open(events_file, 'w') as f:
            json.dump(events_json, f)

        events = gh.aggregate_events(events_json)
        print("Found new events, writing to %s" % path)
        writer.write(events)
        copyfile(events_file, os.path.join(writer.output_path, 'events.json'))


def write_entity(entity=None, repo_folder=None, writer=None):
    try:
        entity_file = open(
            os.path.join(repo_folder, entity + '.json'), 'r')
        entity_decoded = json.load(entity_file)
        if len(entity_decoded) > 0:
            print("Writing %s to %s" % (entity, repo_folder))
            entities = writer.build_rows(entity_decoded)
            writer.write(filename=entity + '.csv', data=entities)
        else:
            print("No %s found in %s" % (entity, repo_folder))
    except FileNotFoundError:
        print("%s.json not found in %s" % (entity, repo_folder))
    return


if __name__ == "__main__":
    main()
