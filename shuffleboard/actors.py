# -*- coding: utf-8 -*-

import click
import csv
# from shutil import copyfile
import json
import os
import re
import requests
import sys

import github_api
import shuffleboard as sb

csv.field_size_limit(sys.maxsize)
HOME = os.getenv("HOME")

@click.command()
@click.option('--gh_api', default=True,
              help='Get project data via GitHub API')
@click.option('--gh_id', help='GitHub OATH2 client id')
@click.option('--gh_secret', help='GitHub OATH2 secret')
@click.option('--actors_file',
              help='Path to list of github usernames to get data on')
@click.option('--repos_file',
              help='Path to list of github repos to create a list of '
                   'usernames to get data on')
def main(gh_api, gh_id, gh_secret, actors_file, repos_file):
    actor_list = []
    contributors = {}
    repo_lookup = {}
    if actors_file:
        actor_folder, end = os.path.split(actors_file)
        f = open(os.path.join(actors_file), 'r')
        actor_list = f.read().splitlines()
    elif repos_file: # build the list of actors

        if github_api is False:  # seriously Python?
            exit("github_api must be True when repo_file is specified")

        actor_folder, end = os.path.split(repos_file)

        # build repo list
        repos = []
        f = open(os.path.join(repos_file), 'r')
        repo_list = f.read().splitlines()
        for r in repo_list:
            (owner, repo) = r.split('/')
            repos.append({'owner': owner, 'repo': repo})

        for r in repos:
            owner = r['owner']
            repo = r['repo']
            repo_slug = '\\'.join([owner, repo])
            repo_resp = get_repo_contributors(
                owner=owner,
                repo=repo,
                params={'client_id': gh_id,'client_secret': gh_secret},
                folder=os.path.join(actor_folder, 'contributors')
            )

            for c in repo_resp:
                if c['login'] in contributors:
                    contributors[c['login']].update({repo_slug: c})
                else:
                    contributors[c['login']] = {repo_slug: c}

        actor_list = list(contributors.keys())

        # dump the combined contributors data to json
        with open(os.path.join(actor_folder, 'contributors',  # TODO mkdir
                               'contributors.json'), 'w') as f:
            json.dump(contributors, f)
    else:
        exit("Please specify a list of usernames or repos using "
             "--actors_file or --repos_file")

    actors_aggr = []
    actor_writer = sb.writer_lookup['repo_owner']

    for a in actor_list:
        if gh_api: # TODO need alternate path
            gh = github_api.GithubGrabber(
                http_client=requests,
                owner=a,
                params={'client_id': gh_id,'client_secret': gh_secret}
            )

            resp = gh.get_entity(entity = "repo_owner")
            out_file = os.path.join(actor_folder, a + '.json')
            print("dumping %s results to file %s" % (a, out_file))

            print("getting %s organizations" % a)

            if 'organizations_url' in resp:
                resp_orgs = gh.get_entity( entity='user_orgs',
                    api_url=resp['organizations_url'])
                out_file_org = os.path.join(
                    actor_folder, a + '_orgs' + '.json')
                print("dumping %s org results to file %s"
                      % (a, out_file_org))
            else:
                resp_orgs = []

            # include orgs as a list in the user's JSON resp
            resp['orgs'] = ','.join([o['login'] for o in resp_orgs])

            # if this is coming from a contributor list, add the repos they are
            # associated with
            if a in contributors:
                resp['repos'] = ','.join(list(contributors[a].keys()))

        # write to csv file
        # TODO: read "resp" from json files if no gh_api
        data = actor_writer.build_rows(resp)
        actor_writer.write(file=os.path.join(
            actor_folder, a + '.csv'), data=data)

        # concat to aggregate python obj
        actors_aggr.append(resp)

    # write aggregate Python obj to csv
    aggr_writer = sb.ListOfDictsCSVWriter()
    all_actors = aggr_writer.build_rows(actors_aggr)
    actor_writer.write(file=os.path.join(
        actor_folder, 'actors.csv'), data=all_actors)


def get_repo_contributors(repo="", owner="", params={}, headers={}, folder=""):
    gh_repo = github_api.GithubGrabber(
        http_client=requests,
        owner=owner,
        repo=repo,
        params=params,
        headers=headers
    )

    resp = gh_repo.get_entity(entity='repo_contributors')

    out_file = os.path.join( folder,
                             '_'.join(['contributors', owner, repo]) + '.json')

    print("dumping %s\%s results to file %s" % (owner, repo, out_file))
    with open(out_file, 'w') as f:
        try:
            json.dump(resp, f)
        except:
            print("unable to serialize %s" % resp)

    return resp

if __name__ == "__main__":
    main()
