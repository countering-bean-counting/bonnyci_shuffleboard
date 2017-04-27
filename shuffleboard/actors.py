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
@click.option('--gh_api', default=False,
              help='Get project data via GitHub API')
@click.option('--gh_id', help='GitHub OATH2 client id')
@click.option('--gh_secret', help='GitHub OATH2 secret')
@click.option('--actors_file',
              help='Path to list of github usernames to get data on')
def main(gh_api, gh_id, gh_secret, actors_file):
    gh_api = True

    if actors_file:
        actor_folder, foo = os.path.split(actors_file)
        f = open(os.path.join(actors_file), 'r')
        actor_list = f.read().splitlines()
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


if __name__ == "__main__":
    main()
