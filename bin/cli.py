# -*- coding: utf-8 -*-

import click
import csv
# from shutil import copyfile
import json
import os
import re
import requests
import sys

from shuffleboard import github_api
import shuffleboard as sb

csv.field_size_limit(sys.maxsize)
HOME = os.getenv("HOME")

# List of what should be fetched from api
# TODO: this should be set by a file or from cli
ENTITIES = []

@click.command()
@click.option('--gh_api', default=False,
              help='Get project data via GitHub API')
@click.option('--json2csv', default=False,
              help='Convert GitHub API JSON to CSV')
@click.option('--gh_path', default=HOME,
              help='Path for JSON data')
@click.option('--repos_file', help='File containing a list of repos: '
                               'username/repo')
@click.option('--owner', help='Org or user for the repo')
@click.option('--repo', help='The repo name (no user or org)')
@click.option('--gh_id', help='GitHub OATH2 client id')
@click.option('--gh_secret', help='GitHub OATH2 secret')
@click.option('--catcsv', default=False,
              help='Combine CSV files with the same name into one')
def main(gh_api, json2csv, gh_path, repos_file, owner, repo, gh_id,
         gh_secret, catcsv):

    # build repo list
    repos = []
    if repos_file:
        f = open(os.path.join(gh_path, repos_file), 'r')
        repo_list = f.read().splitlines()
        for r in repo_list:
            (owner, repo) = r.split('/')
            repos.append({'owner': owner, 'repo': repo})
    else:
        repos.append({'owner': owner, 'repo': repo})

    if gh_api:
        for r in repos:
            do_gh_api(repo=r['repo'],
                      owner=r['owner'],
                      gh_path=gh_path,
                      params={'client_id': gh_id, 'client_secret': gh_secret},
                      entities=ENTITIES,
                      headers={
                          'Accept':'application/vnd.github.loki-preview+json'}
                      )

    if json2csv or catcsv:
        # currently assumes data for each repo is stored in a folder structure
        #  with user or org as top level and all repos at the next level
        # if the repo belongs to an org, the topmost folder must be the org
        # name

        csv_files = {}

        # get a list of all folders at the top level of the directory
        gh_archive_folder = gh_path
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

            # get the current directory
            path1, end = os.path.split(row[0])
            # get the parent directory for comparison
            path2, parent = os.path.split(path1)

            # check if it's a user level directory
            # exclude repos with the same name as the user
            if (end in users) and (parent != end):
                owner = end
                folders[owner] = {'repos': {r: None for r in row[1]},
                                  **walk_data}
            else:
                if parent in users:  # check if it's a repo level one
                    owner = parent
                    repo = end
                    # double check this is a legit repo
                    if repo in folders[owner]['repos'] and len(row[2]) > 0:
                        folders[owner]['repos'][repo] = walk_data
                else:
                    print("didn't recognize path as user or repo: %s" % row[0])

        for owner, walk_data in folders.items():
            # NOTE: removed events section because we can get events data from
            # Google BigQuery

            # for each directory
            for repo, repo_walk_data in walk_data['repos'].items():
                repo_folder = repo_walk_data['path']

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
                    if json2csv:
                        if entity in sb.writer_lookup:
                            entity_writer = sb.writer_lookup[entity]
                        else:
                            entity_writer = sb.CSVWriter()
                    if len(entity_file_list) == 1:  # just one data file
                        entity_file = entity_file_list[0]
                        if catcsv:
                            entity_filename, ext = \
                                os.path.splitext(entity_file)

                            if entity in csv_files:
                                csv_files[entity].append(entity_filename +
                                                         '.csv')
                            else:
                                csv_files[entity] = [entity_filename + '.csv']
                        if json2csv:
                            write_entity(entity_file=entity_file,
                                         writer=entity_writer)
                    else:  # multiple files need to be combined
                        if json2csv:
                            entities = entity_writer.build_rows(
                                get_entity_list(entity_file_list))
                            entity_writer.write(file=os.path.join(
                                repo_folder, entity + '.csv'), data=entities)

    if catcsv:
        for entity, files in csv_files.items():
            print("Combining csv files for %s " % entity)

            header_row = []
            csv_combined = []
            null_repos = []
            for file in files:
                print("Reading in %s " % file)

                # get the owner and repo name
                filepath, filename = os.path.split(file)
                path, repo_slug2 = os.path.split(filepath)
                path, repo_slug1 = os.path.split(path)
                repo_slug = "%s/%s" % (repo_slug1, repo_slug2)

                # read in csv file contents
                try:
                    f = open(file, 'r')
                    file_contents = csv.reader(f, delimiter=',', quotechar='"')

                # if a json file doesn't have an associated csv file,
                # it means there wasn't data for that repo. We need to add
                # this in later as a row of null values
                except FileNotFoundError:
                    print("%s not found" % file)
                    null_repos.append(repo_slug)
                    continue

                # if this is the first entry, keep the header row
                next_row = file_contents.__next__()
                if len(csv_combined) == 0:
                    header_row = next_row
                    header_row += ["repo_slug", "repo_slug1", "repo_slug2"]
                    csv_combined.append(header_row)

                for row in file_contents:
                    row += [repo_slug, repo_slug1, repo_slug2]
                    csv_combined.append(row)

            # add rows for null repos
            for r in null_repos:
                null_row = []
                # add a blank value for each column except the last one
                for i in header_row[:-3]:
                    null_row.append("")
                # tack on the repo slug
                repo_slug1, repo_slug2 = r.split('/')
                null_row += [r, repo_slug1, repo_slug2]
                if filename == "repo_data.csv":
                    print("Adding row to %s for null repo %s/%s" %
                      (filename, repo_slug1, repo_slug2))
                # add the row for that repo to the main spreadsheet
                csv_combined.append(null_row)

            # write to gh_archive_folder
            catcsv_file = os.path.join(gh_archive_folder, filename)
            with open(catcsv_file, 'w') as f:
                print("Writing combined csv file %s " % catcsv_file)
                writer = csv.writer(f, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_ALL)
                for row in csv_combined:
                    writer.writerow(row)


def write_entity(entity_file=None, writer=None):
    entity_filename, ext = os.path.splitext(entity_file)
    repo_path, entity = os.path.split(entity_filename)
    entity_csv_file = entity_filename + '.csv'

    try:
        json_file = open(entity_file, 'r')
        entity_decoded = json.load(json_file)
        if (len(entity_decoded) > 0) and 'no_' + entity not in entity_decoded:
            print("Writing %s" % entity_csv_file)
            entities = writer.build_rows(entity_decoded)
            writer.write(file=entity_csv_file,
                         data=entities)
        else:
            # TODO: write a csv file with the entity name
            print("empty json file %s" % entity_file)
    except FileNotFoundError:
        print("%s not found" % entity_file)
    except json.decoder.JSONDecodeError:
        print("json decoding error for %s: %s"
              % (entity_file, json.decoder.JSONDecodeError))
    return entity_csv_file


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


# TODO: break this up into something more modular
# this is literally a sloppy copy pasta job
def do_gh_api(entities=[],
              repo='', owner='', gh_path='', params={}, headers={}):
    # make folder for project
    repo_folder = os.path.join(gh_path, owner, repo)
    os.makedirs(repo_folder, exist_ok=True)

    gh = github_api.GithubGrabber(
        http_client=requests,
        owner=owner,
        repo=repo,
        params=params,
        headers=headers
    )

    repo_result = gh.get_multiple(entities=entities)

    for (entity, resp) in repo_result.items():
        out_file = os.path.join(repo_folder, entity + '.json')
        print("dumping %s results to file %s" % (entity, out_file))
        with open(out_file, 'w') as f:
            try:
                json.dump(resp, f)
            except:
                print("unable to serialize %s" % resp)
    return

if __name__ == "__main__":
    main()
