# -*- coding: utf-8 -*-

import click

from shuffleboard import meatmap as meatmap_lib

# List of what should be fetched from api
# TODO: these should be set by a file or from cli
ENTITIES = ['groups_find_bdd']


@click.command()
@click.option('--meetup_api_key', default="NULL",
              help='Meetup API Key')
@click.option('--meetup_folder', default="",
              help='Results output destination')
def main(meetup_api_key, meetup_folder):
    meatmap = meatmap_lib.Meatmap()
    meatmap.fetch_data(api_key=meetup_api_key,
                     folder=meetup_folder,
                     entities=ENTITIES)

if __name__ == "__main__":
    main()
