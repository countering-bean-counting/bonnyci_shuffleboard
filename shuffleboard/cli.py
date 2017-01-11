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
    # for updating an existing project based on event activity
    # project = "BonnyCI"
    path = '/home/auggy/dev/BonnyCI/shuffleboard_data'  # TODO env var option
    use_etag = True
    read_from_file = False
    read_from_file_name = 'events.json'

    # for creating a new github archive sample set
    # currently assumes data for each repo is stored in a folder structure
    #  with user or org as top level and all repos at the next level
    # if the repo belongs to an org, the topmost folder must be the org name
    gh_archive_folder = '/home/auggy/dev/BonnyCI/shuffleboard_data/gh_archive'
    gh_archive_import = True

    if gh_archive_import:
        # get a list of all folders at the top level of the directory
        # these should be organizations and usernames
        walk = tuple(os.walk(gh_archive_folder))
        users = walk[0][1]

        # make a dict organized by org name and repo name
        folders = {}
        for idx, row in enumerate(walk):

            walk_data = {
                'path': row[0],
                'files': row[2],
                'walk_idx': idx
            }

            path, end = os.path.split(row[0])
            # check if it's a user level directory
            if end in users:
                user = end
                folders[user] = {'repos': {r : None for r in row[1]},
                                 **walk_data }
            else:
                path2, end2 = os.path.split(path)
                if end2 in users: # check if it's a repo level one
                    user = end2
                    repo = end
                    # double check this is a legit repo
                    if repo in folders[user]['repos'] and len(row[2]) > 0:
                        folders[user]['repos'][repo] = walk_data
                else:
                    print("didn't recognize path as user or repo: %s" % row[0])

        for user, walk_data in folders.items():
            # make a list of files that start with "event" and end with "json"
            gh_archive_user_folder = walk_data['path']
            event_files = \
                [os.path.join(gh_archive_user_folder, f)
                for f in walk_data['files']
                if os.path.splitext(f)[0][:5] == 'event'
                and os.path.splitext(f)[1] == '.json']

            events_list = get_entity_list(event_files)

            gh = github_api.GithubGrabber()
            print("Writing events to %s" % gh_archive_user_folder)
            events = gh.aggregate_events(events_list)
            events_writer = sb.EventsCSVWriter()
            events_writer.write(out_path=gh_archive_user_folder,
                                events=events)

            # for each directory
            for repo, repo_walk_data in walk_data['repos'].items():
                repo_folder = repo_walk_data['path']
                csv_writer = sb.CSVWriter(repo_folder)

                # create a list of json files keyed by entity
                # if we have a lot of values, the github api limits how many
                # can be returned in one call. These would be downloaded via
                # different call to different files formatted as
                # entity1.json,..,entityn.json.
                entity_files = {}
                for f in repo_walk_data['files']:
                    base, ext = os.path.splitext(f)
                    if ext == '.json':
                        # remove any numbers from the base name
                        entity_name = re.sub(r'\d', '', base)
                        if entity_name in entity_files:
                            entity_files[entity_name].append(
                                os.path.join(repo_folder, f))
                        else:
                            entity_files[entity_name] = \
                                [os.path.join(repo_folder, f)]

                for entity, entity_file_list in entity_files.items():
                    print("Processing %s for repo %s" % (entity, repo))
                    if len(entity_file_list) == 1: # just one data file
                        entity_file = entity_file_list[0]
                        write_entity(entity_file=entity_file,
                                     writer=sb.CSVWriter())
                    else: # multiple files need to be combined
                        entity_writer = sb.CSVWriter()
                        entities = entity_writer.build_rows(
                            get_entity_list(entity_file_list))
                        entity_writer.write(file=os.path.join(
                            repo_folder, entity + '.csv'), data=entities)

    # don't run the rest of the script
    exit("Finished")

# TODO: this code doesn't work anymore
    # # TODO move logic to get continuous updates to a new cli program
    # # TODO fix this to take in a list of user/repo's and an optional list of
    # #  entities to pull via the api
    # header_file = os.path.join(path, 'gh_headers')
    # with open(header_file, 'r') as f:
    #     last_headers = json.load(f)
    #     etag = last_headers["ETag"][2:]
    #
    # # TODO set the writer instance type based on command line args
    # # cli_writer = sb.EventsCLIWriter(printer=print)
    # csv_writer = sb.EventsCSVWriter(out_path=path)
    # writer = csv_writer
    #
    # header_writer = sb.GhHeaderTxtFileWriter(out_path=path,
    #                                          filename='gh_headers')
    #
    # if read_from_file:
    #     # read in json file
    #     events_file = os.path.join(path, read_from_file_name)
    #     print("reading events from file %s" % events_file)
    #     # combine file contents into one json structure
    #     f = open(events_file, 'r')
    #     content = f.read()
    #     if re.match('\[', content):
    #         parsed_content = json.loads(content)
    #         events_json = parsed_content
    #     else:
    #         parsed_content = '[' + '},{'.join(content.split('}\n{')) + ']'
    #         events_json = json.loads(parsed_content)
    #
    #     gh = github_api.GithubGrabber()
    #
    # else:
    #     gh = github_api.GithubGrabber(http_client=requests)
    #
    #     events_args = {}
    #     if use_etag:
    #         events_args['etag'] = etag
    #
    #     events_json = gh.get_events(**events_args)
    #     header_writer.write(gh.headers)
    #
    # if 'no_events' in events_json:
    #     print("No events received %s" % list(events_json.values()))
    # else:
    #     # dump json response to file in case something fails
    #     events_out_file = os.path.join(path, 'events.json')
    #     print("dumping events to file %s" % events_out_file)
    #     with open(events_out_file, 'w') as f:
    #         json.dump(events_json, f)
    #
    #     events = gh.aggregate_events(events_json)
    #     print("Found new events, writing to %s" % path)
    #     writer.write(events)
    #     copyfile(events_out_file, os.path.join(writer.output_path,
    #                                            'events.json'))


def write_entity(repo_path=None, entity_file=None, writer=None):
    try:
        file = open(entity_file, 'r')
        entity_decoded = json.load(file)
        if len(entity_decoded) > 0:
            entity, ext = os.path.splitext(entity_file)
            print("Writing %s" % entity + '.csv')
            entities = writer.build_rows(entity_decoded)
            writer.write(file=os.path.join(repo_path, entity + '.csv'),
                         data=entities)
        else:
            print("empty json file %s" % entity_file)
    except FileNotFoundError:
        print("%s not found" % entity_file)
    except json.decoder.JSONDecodeError:
        print("json decoding error for %s: %s"
              % (entity_file, json.decoder.JSONDecodeError))
    return


def get_entity_list(entity_files):
    entity_list = []
    for entity_file in entity_files:
        print("reading file %s", entity_file)
        # combine file contents into one json structure
        f = open(entity_file, 'r')
        content = f.read()
        # the json is properly formatted as a list if it came from a
        # github api call
        if re.match('\[', content):
            parsed_content = json.loads(content)
        else:  # json from Github Archive is not a valid list
            # row is a json object deliminated by a new line
            parsed_content = \
                json.loads('[' + '},{'.join(content.split('}\n{')) + ']')
        entity_list += parsed_content
    return entity_list


if __name__ == "__main__":
    main()
