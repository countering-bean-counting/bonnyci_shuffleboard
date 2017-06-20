# -*- coding: utf-8 -*-
# Utility functions for accessing the meetup api and processing api data

import json
import os
import requests

from shuffleboard import meetup_api
from shuffleboard import shuffleboard as sb


class Meatmap:

    def fetch_data(self,
                   api_key='',
                   folder='',
                   entities=[],
                   prefix='',
                   endpoint='',
                   extra_fields=[]  # present in some responses but not others
                   ):
        for entity in entities:

            json_file = os.path.join(folder, prefix + entity + '.json')
            csv_file = os.path.join(folder, prefix + entity + '.csv')
            args = {'entity': entity}

            if api_key != "NULL" and api_key:
                meetup = meetup_api.MeetupAPIClient(
                    http_client=requests,
                    headers={},
                    params={'key': api_key,
                            'sign': "true",
                            'page': 200  # TODO if > 200 need to handle offset
                            }
                )

                if endpoint:
                    api_url = meetup.meetup_api_base + endpoint
                    args['api_url'] = api_url

                resp = meetup.get_entity(**args)

                print("dumping %s results to file %s" % (entity, json_file))
                with open(json_file, 'w') as f:
                    try:
                        json.dump(resp, f)
                    except:
                        print("unable to serialize %s" % resp)

            # build CSV file
            if api_key == "NULL" or not api_key:
                # if no api key, read resp from meetup_folder
                resp = json.load(open(json_file, 'r'))

            print("writing %s results to csv file %s" % (entity, csv_file))
            csv_writer = sb.MeatmapCSVWriter()
            resp_sheet = csv_writer.build_rows(data=resp, extra=extra_fields)
            csv_writer.write(file=csv_file, data=resp_sheet)
            return

    def get_current_groups(self, meetup_api_key):

        if meetup_api_key == "NULL":
            print("No meetup api key")
            return {}

        meetup = meetup_api.MeetupAPIClient(
            http_client=requests,
            headers={},
            params={'key': meetup_api_key,
                    'sign': "true",
                    }
        )

        current_groups_resp = meetup.get_entity(entity='groups_self')
        current_groups = {g['urlname']: g for g in current_groups_resp}
        return current_groups
