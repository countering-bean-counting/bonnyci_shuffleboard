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
@click.option('--catcsv', default=True,
              help='Combine existing CSV files')
@click.option('--gh_id', help='GitHub OATH2 client id')
@click.option('--gh_secret', help='GitHub OATH2 secret')
@click.option('--repos_file',
              help='Path to csv of github repos and status api urls')
def main(gh_api, catcsv, gh_id, gh_secret, repos_file):

    if repos_file:
        repo_folder, foo = os.path.split(repos_file)
        f = open(repos_file, 'r')
        repo_list = csv.reader(f, delimiter=',')
        statuses_aggr = []
        statuses_aggr_header_row = []
        null_repos = []
        statuses_writer = sb.writer_lookup['statuses']

        if gh_api:
            for row in repo_list:
                (repo_slug, api_url) = row
                (owner, repo) = repo_slug.split('/')

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
                    null_repos.append(repo_slug)
                    continue

                # write to csv file
                # TODO: read "resp" from json files if no gh_api
                if len(resp) == 0:
                    null_repos.append(repo_slug)
                else:
                    data = statuses_writer.build_rows(resp)
                    statuses_writer.write(file=os.path.join(
                        repo_folder, owner + '-' + repo + '.csv'), data=data)

        # write aggregate Python obj to csv
        if catcsv:
            # TODO: reset repo_list so the iterator is back at the beginning
            repo_pr_statuses = []

            # build aggregated statuses list
            for row in repo_list:
                (repo_slug, api_url) = row
                (owner, repo) = repo_slug.split('/')
                statuses_file = "%s-%s.csv" % (owner, repo)

                try:
                    f = open(os.path.join(repo_folder, statuses_file), 'r')
                    file_contents = csv.reader(f, delimiter=',')

                # if no csv file, it means there wasn't data for that
                # repo. We need to add this in later as a row of null
                # values
                except FileNotFoundError:
                    print("%s not found" % statuses_file)
                    null_repos.append(repo_slug)
                    continue

                # set up header row and append to main list
                next_row = file_contents.__next__()
                if len(statuses_aggr_header_row) == 0:
                    statuses_aggr_header_row = next_row
                    statuses_aggr_header_row += \
                        ["repo_slug", "owner", "repo"]
                    repo_pr_statuses.append(statuses_aggr_header_row)

                # add the repo names so we can distinguish between them in
                # the combined file
                for status_row in file_contents:
                    statuses_aggr.append(
                        status_row + [repo_slug, owner, repo])

            # append aggregated statuses to main list
            repo_pr_statuses += statuses_aggr

            # add rows for null repos
            for null_repo in null_repos:
                null_row = []
                # add a blank value for each column except the last one
                for i in statuses_aggr_header_row[:-3]:
                    null_row.append("")
                # tack on the repo slug
                repo_slug1, repo_slug2 = null_repo.split('/')
                null_row += [null_repo, repo_slug1, repo_slug2]
                print("Adding row for null repo %s" % null_repo)
                # add the row for that repo to the main spreadsheet
                repo_pr_statuses.append(null_row)

            # write to gh_archive_folder
            catcsv_file = os.path.join(repo_folder, 'repo_pr_statuses.csv')
            with open(catcsv_file, 'w') as f:
                print("Writing combined csv file %s " % catcsv_file)
                writer = csv.writer(f, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_ALL)
                for row in repo_pr_statuses:
                    writer.writerow(row)


if __name__ == "__main__":
    main()
