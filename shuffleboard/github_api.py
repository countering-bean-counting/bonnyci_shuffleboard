# -*- coding: utf-8 -*-


# Class to handle getting Github data at the repository level

class GithubGrabber:
    def __init__(self,
                 params = {},
                 headers = {},
                 owner='',
                 repo = '',
                 http_client=None,
                 gh_api_base='https://api.github.com'):

        self.owner = owner
        self.repo = repo
        self.gh_api_base = gh_api_base
        self.http_client = http_client
        self.params = params
        self.headers = headers

        self.endpoint_lookup = {
            'repo_owner': '/users/%s' % self.owner,
            'repo_data': '/repos/%s/%s' % (self.owner, self.repo),
            'repo_releases': '/repos/%s/%s/releases' % (self.owner, self.repo),
            'repo_readme': '/repos/%s/%s/readme' % (self.owner, self.repo),
            'repo_languages':
                '/repos/%s/%s/languages' % (self.owner, self.repo),
            'repo_pulls': '/repos/%s/%s/pulls' % (self.owner, self.repo),
            'yml_travis':
                '/repos/%s/%s/contents/.travis.yml' % (self.owner, self.repo),
            'yml_circleci':
                '/repos/%s/%s/contents/circle.yml' % (self.owner, self.repo),
            'yml_appveyor':
                '/repos/%s/%s/contents/appveyor.yml' % (self.owner, self.repo),
            'yml_probo':
                '/repos/%s/%s/contents/.probo.yml' % (self.owner, self.repo),
            'Jenkinsfile':
                '/repos/%s/%s/contents/Jenkinsfile' % (self.owner, self.repo),
            'yml_gitlab':
                '/repos/%s/%s/contents/.gitlab-ci.yml' %
                (self.owner, self.repo)
        }

        self.entity_lookup = {
            'statuses': {
                'fn': lambda x: self.get_statuses_from_pulls(pulls=x['pulls']),
                'depends_on': 'pulls' # TODO this may need to support multiple
            }
        }

    def _get(self, url):
        response = self.http_client.get(url,
                                        headers=self.headers,
                                        params=self.params)
        self.resp_headers = response.headers
        return response

    def get_entity(self, entity='', api_url=''):
        # TODO: this should be a proper warning
        if not entity:
            print("no entity specified for get_entity()")
            return

        if not api_url:
            endpoint = self.endpoint_lookup[entity]
            api_url = self.gh_api_base + endpoint

        response = self._get(api_url)
        if response.status_code != 200:
            return {'no_%s' % entity: "%s %s" %
                                      (str(response.status_code), response)}
        else:
            return response.json()

    def get_multiple(self, entities=[]):
        result = {}
        if len(entities) == 0:
            entities = self.endpoint_lookup.keys()

        for entity in entities:
            if entity not in self.entity_lookup:
                result[entity] = self.get_entity(entity=entity)
            else:
                if self.entity_lookup[entity]['depends_on']:
                    if self.entity_lookup[entity]['depends_on'] not in result:
                        result[self.entity_lookup[entity]['depends_on']] = []

                result[entity] = self.entity_lookup[entity]['fn'](result)

        return result

    def get_statuses_from_pulls(self, pulls=[]):
        # get pulls
        if len(pulls) == 0:
            pulls = self.get_entity(entity='repo_pulls')

        if len(pulls) == 0 or 'no_repo_pulls' in pulls:
            return pulls # if there are no pulls, there are no statuses

        # extract the status url from the first entry
        statuses_url = pulls[0]['statuses_url']

        result = self.get_entity(entity='statuses',
                                 api_url=statuses_url)

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

