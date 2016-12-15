# -*- coding: utf-8 -*-

import click
import github_api

repos = ['shuffleboard']


@click.command()
def main(args=None):

    for repo in repos:
        gh = github_api.GithubGrabber(repo)
        issues = gh.get_issues()

        for i in issues:
            print(vars(i))


if __name__ == "__main__":
    main()
