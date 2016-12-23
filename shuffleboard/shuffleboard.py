# -*- coding: utf-8 -*-
import requests
import pprint

import github_api
import plunder


class EventsCLIWriter(plunder.CLIWriter):

    def __init__(self):
        super()
        self.printer = pprint.pprint

    def write(self, events):
        for (repo, typed_events) in events.items():
            self.printer(repo)
            for (typed_event_name, event_list) in typed_events.items():
                self.printer(typed_event_name)
                self.printer(event_list, depth=3)
