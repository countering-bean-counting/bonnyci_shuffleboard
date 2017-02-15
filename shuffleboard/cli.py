# -*- coding: utf-8 -*-

import click
# from shutil import copyfile
import json
import os
import re
import requests

import github_api
import shuffleboard as sb

HOME = os.getenv("HOME")

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
def main(gh_api, json2csv, gh_path, repos_file, owner, repo, gh_id, gh_secret):

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
            do_gh_api(repo = r['repo'],
                      owner = r['owner'],
                      gh_path = gh_path,
                      params = {'client_id': gh_id, 'client_secret': gh_secret}
                      )

    if json2csv:
        # currently assumes data for each repo is stored in a folder structure
        #  with user or org as top level and all repos at the next level
        # if the repo belongs to an org, the topmost folder must be the org
        # name

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

            path, end = os.path.split(row[0])
            # check if it's a user level directory
            if end in users:
                owner = end
                folders[owner] = {'repos': {r: None for r in row[1]},
                                  **walk_data}
            else:
                path2, end2 = os.path.split(path)
                if end2 in users:  # check if it's a repo level one
                    owner = end2
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
                    if entity in sb.writer_lookup:
                        entity_writer = sb.writer_lookup[entity]
                    else:
                        entity_writer = sb.CSVWriter()
                    if len(entity_file_list) == 1:  # just one data file
                        entity_file = entity_file_list[0]
                        write_entity(entity_file=entity_file,
                                     writer=entity_writer)
                    else:  # multiple files need to be combined
                        entities = entity_writer.build_rows(
                            get_entity_list(entity_file_list))
                        entity_writer.write(file=os.path.join(
                            repo_folder, entity + '.csv'), data=entities)


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


# TODO: break this up into something more modular
# this is literally a sloppy copy pasta job
def do_gh_api(repo='', owner='', gh_path='', params={}, headers={}):
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

    repo_result = gh.get_all()
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
