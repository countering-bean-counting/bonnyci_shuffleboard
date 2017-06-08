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

    if actors_file:
        actor_folder, end = os.path.split(actors_file)
        f = open(os.path.join(actors_file), 'r')
        actor_list = sorted(f.read().splitlines())

    elif repos_file:  # build the list of actors

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

        actor_list = sorted(list(contributors.keys()))

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
        if gh_api:  # TODO need alternate path
            gh = github_api.GithubGrabber(
                http_client=requests,
                owner=a,
                params={'client_id': gh_id,'client_secret': gh_secret}
            )

            resp = gh.get_entity(entity = "repo_owner")
            out_file = os.path.join(actor_folder, 'actor_' + a + '.json')
            print("dumping %s results to file %s" % (a, out_file))
            with open(out_file, 'w') as f:
                json.dump(resp, f)

            print("getting %s organizations" % a)

            if 'organizations_url' in resp:
                resp_orgs = gh.get_entity( entity='user_orgs',
                    api_url=resp['organizations_url'])
                out_file_org = os.path.join(
                    actor_folder, 'actor_' + a + '_orgs' + '.json')
                print("dumping %s org results to file %s"
                      % (a, out_file_org))
                with open(out_file_org, 'w') as f:
                    json.dump(resp, f)
            else:
                resp_orgs = []

            # include orgs as a list in the user's JSON resp
            resp['public_orgs'] = ','.join([o['login'] for o in resp_orgs])

            # get names/emails from commit history
            emails = get_email_from_commits(gh_api = gh, folder=actor_folder)
            resp['commits_names'] = ','.join([n for n in emails['names']])
            resp['commits_emails'] = ','.join([e for e in emails['emails']])

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


def get_email_from_commits(gh_api="", folder=""):

    emails = {'names': {}, 'emails': {}}

    # get repos
    repos = gh_api.get_entity(entity='owner_repos')
    out_file = os.path.join(folder, 'actor_repos_' + gh_api.owner + '.json')

    if not isinstance(repos, list) or len(repos) == 0:
        print("No repos found for %s: %s" % (gh_api.owner, repos))
        return emails
    else:
        print("dumping %s repos results to file %s" % (gh_api.owner, out_file))
        with open(out_file, 'w') as f:
            try:
                json.dump(repos, f)
            except:
                print("unable to serialize %s" % repos)

    # for each repo get commits by owner
    for r in repos:
        print("getting commits for %s from %s" % (gh_api.owner, r['name']))
        gh_commits = github_api.GithubGrabber(
            http_client=requests,
            params={**gh_api.params, 'author': gh_api.owner},
            headers=gh_api.headers,
            owner=gh_api.owner,
            repo=r['name']
        )
        commits_url = re.sub(r'\{\/sha\}', '', r['commits_url'])
        try:
            commits = gh_commits.get_entity(entity='owner_repo_commits',
                                        api_url=commits_url)
        except:
            print("error getting commits: ", sys.exc_info()[0])
            continue

        if not isinstance(commits, list) or len(commits) == 0:
            print("No commits found for %s in %s" % (gh_api.owner, r['name']))
            continue
        else:
            commits_file = os.path.join(folder, '_'.join(
                ['actor', 'commits', gh_api.owner, r['name']]) + '.json')
            print("dumping %s commits results to file %s" %
                  (gh_api.owner, commits_file))
            with open(commits_file, 'w') as f:
                try:
                    json.dump(commits, f)
                except:
                    print("unable to serialize %s" % commits)

        # for each commit extract name/email
        for c in commits:
            com = c['commit']['author']
            # use a dict so they stay unique
            if com['name'] in emails['names']:
                emails['names'][com['name']] += 1
            else:
                emails['names'][com['name']] = 1
                print("New name for %s in %s: %s" %
                      (gh_api.owner, r['name'], com['name']))

            if com['email'] in emails['emails']:
                emails['emails'][com['email']] += 1
            else:
                emails['emails'][com['email']] = 1
                print("New email for %s in %s: %s" %
                      (gh_api.owner, r['name'], com['email']))

    return emails

if __name__ == "__main__":
    main()
