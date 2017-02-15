# -*- coding: utf-8 -*-


# Class to handle getting Github data at the repository level

class GithubGrabber:
    def __init__(self,
                 page=100,
                 owner='',
                 repo = '',
                 http_client=None,
                 gh_api_base='https://api.github.com'):

        self.owner = owner
        self.repo = repo
        self.gh_api_base = gh_api_base
        self.http_client = http_client
        self.page = 100
        self.headers = {}

        self.endpoint_lookup = {
            'repo_owner': '/users/%s' % self.owner,
            'repo_data': '/repos/%s/%s' % (self.owner, self.repo),
            'repo_releases': '/repos/%s/%s/releases' % (self.owner, self.repo),
            'repo_readme': '/repos/%s/%s/readme' % (self.owner, self.repo),
            'repo_languages':
                '/repos/%s/%s/languages' % (self.owner, self.repo),
            'repo_contributors':
                '/repos/%s/%s/stats/contributors' % (self.owner, self.repo)
        }

    def _get(self, url, headers={}):
        response = self.http_client.get(url, headers=headers)
        self.headers = response.headers
        return response

    def get_entity(self, headers={}, entity=''):
        endpoint = self.endpoint_lookup[entity] # host is turning into host='api.github.comrepos', port=443): Max retries exceeded with url: /BonnyCI/hoist/stats/contributors
        response = self._get(self.gh_api_base + endpoint,
                             headers=headers)
        if response.status_code != 200:
            return {'no_%s' % entity: response}
        else:
            return response.json()

    def get_all(self, headers={}):
        result = {}
        for entity in self.endpoint_lookup.keys():
            result[entity] = self.get_entity(entity=entity, headers=headers)
        return result

    # TODO: update this to use get_entity
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

