# -*- coding: utf-8 -*-


# Class to handle getting Github data at the repository level

class GithubGrabber:
    def __init__(self,
                 page=100,
                 owner='BonnyCI',
                 http_client=None,
                 gh_api_base='https://api.github.com'):

        self.owner = owner
        self.gh_api_base = gh_api_base
        self.http_client = http_client
        self.page = 100
        self.headers = {}

    def _get(self, url, headers={}):
        response = self.http_client.get(url, headers=headers)
        self.headers = response.headers
        return response

    # get events and group by type
    def get_events(self, etag=None):
        headers = {}
        if etag:
            headers['If-None-Match'] = etag
        events_endpoint = '/users/%s/events' % self.owner
        response = self._get(self.gh_api_base + events_endpoint,
                             headers=headers)
        if response.status_code != 200:
            return {'no_events': response}
        else:
            return response.json()
