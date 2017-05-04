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
@click.option('--gh_api', default=False,
              help='Get project data via GitHub API')
@click.option('--gh_id', help='GitHub OATH2 client id')
@click.option('--gh_secret', help='GitHub OATH2 secret')
@click.option('--repos_file',
              help='Path to csv of github repos and status api urls')
def main(gh_api, gh_id, gh_secret, repos_file):
    gh_api = True

    if repos_file:
        repo_folder, foo = os.path.split(repos_file)
        f = open(repos_file, 'r')
        repo_list = csv.reader(f, delimiter=',')
        statuses_aggr = []
        statuses_writer = sb.writer_lookup['statuses']

        for row in repo_list:
            (repo_slug, api_url) = row
            (owner, repo) = repo_slug.split('/')
            if gh_api: # TODO need alternate path
                gh = github_api.GithubGrabber(
                    http_client=requests,
                    owner=owner,
                    repo=repo,
                    params={'client_id': gh_id,'client_secret': gh_secret}
                )

                resp = gh.get_entity(entity = "statuses",
                                     api_url=api_url)
                out_file = os.path.join(repo_folder, owner + '-' + repo +
                                        '.json')
                print("dumping %s results to file %s" % (repo_slug, out_file))
                with open(out_file, 'w') as f:
                    try:
                        json.dump(resp, f)
                    except:
                        print("unable to serialize %s" % resp)

                if not (isinstance(resp, list) and len(resp) > 0):
                    continue

                # write to csv file
                # TODO: read "resp" from json files if no gh_api
                data = statuses_writer.build_rows(resp)
                statuses_writer.write(file=os.path.join(
                    repo_folder, owner + '-' + repo + '.csv'), data=data)

                # concat to aggregate python obj
                statuses_aggr.append(resp)

        # TODO this is a list of lists of dicts, it doesn't work
        # write aggregate Python obj to csv
        aggr_writer = sb.ListOfDictsCSVWriter()
        all_statuses = aggr_writer.build_rows(statuses_aggr)
        statuses_writer.write(file=os.path.join(repo_folder, 'statuses.csv'),
                              data=all_statuses)


if __name__ == "__main__":
    main()
