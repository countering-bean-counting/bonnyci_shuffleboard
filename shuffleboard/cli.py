# -*- coding: utf-8 -*-

import click
import github_api

repos = ['projman']


@click.command()
def main(args=None):

    for repo in repos:

        issues = github_api.get_github_issues_for_repo(repo)

        for i in issues:
            print(vars(i))


if __name__ == "__main__":
    main()
