# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

from keystoneauth1 import access
from keystoneauth1 import exceptions
from keystoneauth1 import fixture
from keystoneauth1.tests.unit import utils


class ServiceCatalogTest(utils.TestCase):
    def setUp(self):
        super(ServiceCatalogTest, self).setUp()

        self.AUTH_RESPONSE_BODY = fixture.V3Token(
            audit_chain_id=uuid.uuid4().hex)
        self.AUTH_RESPONSE_BODY.set_project_scope()

        self.AUTH_RESPONSE_BODY.add_role(name='admin')
        self.AUTH_RESPONSE_BODY.add_role(name='member')

        s = self.AUTH_RESPONSE_BODY.add_service('compute', name='nova')
        s.add_standard_endpoints(
            public='https://compute.north.host/novapi/public',
            internal='https://compute.north.host/novapi/internal',
            admin='https://compute.north.host/novapi/admin',
            region='North')

        s = self.AUTH_RESPONSE_BODY.add_service('object-store', name='swift')
        s.add_standard_endpoints(
            public='http://swift.north.host/swiftapi/public',
            internal='http://swift.north.host/swiftapi/internal',
            admin='http://swift.north.host/swiftapi/admin',
            region='South')

        s = self.AUTH_RESPONSE_BODY.add_service('image', name='glance')
        s.add_standard_endpoints(
            public='http://glance.north.host/glanceapi/public',
            internal='http://glance.north.host/glanceapi/internal',
            admin='http://glance.north.host/glanceapi/admin',
            region='North')

        s.add_standard_endpoints(
            public='http://glance.south.host/glanceapi/public',
            internal='http://glance.south.host/glanceapi/internal',
            admin='http://glance.south.host/glanceapi/admin',
            region='South')

        s = self.AUTH_RESPONSE_BODY.add_service('block-storage', name='cinder')
        s.add_standard_endpoints(
            public='http://cinder.north.host/cinderapi/public',
            internal='http://cinder.north.host/cinderapi/internal',
            admin='http://cinder.north.host/cinderapi/admin',
            region='North')

        s = self.AUTH_RESPONSE_BODY.add_service('volumev2', name='cinder')
        s.add_standard_endpoints(
            public='http://cinder.south.host/cinderapi/public/v2',
            internal='http://cinder.south.host/cinderapi/internal/v2',
            admin='http://cinder.south.host/cinderapi/admin/v2',
            region='South')

        s = self.AUTH_RESPONSE_BODY.add_service('volumev3', name='cinder')
        s.add_standard_endpoints(
            public='http://cinder.south.host/cinderapi/public/v3',
            internal='http://cinder.south.host/cinderapi/internal/v3',
            admin='http://cinder.south.host/cinderapi/admin/v3',
            region='South')

        self.north_endpoints = {'public':
                                'http://glance.north.host/glanceapi/public',
                                'internal':
                                'http://glance.north.host/glanceapi/internal',
                                'admin':
                                'http://glance.north.host/glanceapi/admin'}

        self.south_endpoints = {'public':
                                'http://glance.south.host/glanceapi/public',
                                'internal':
                                'http://glance.south.host/glanceapi/internal',
                                'admin':
                                'http://glance.south.host/glanceapi/admin'}

    def test_building_a_service_catalog(self):
        auth_ref = access.create(auth_token=uuid.uuid4().hex,
                                 body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        self.assertEqual(sc.url_for(service_type='compute'),
                         "https://compute.north.host/novapi/public")
        self.assertEqual(sc.url_for(service_type='compute',
                                    interface='internal'),
                         "https://compute.north.host/novapi/internal")

        self.assertRaises(exceptions.EndpointNotFound,
                          sc.url_for,
                          region_name='South',
                          service_type='compute')

    def test_service_catalog_endpoints(self):
        auth_ref = access.create(auth_token=uuid.uuid4().hex,
                                 body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        public_ep = sc.get_endpoints(service_type='compute',
                                     interface='public')
        self.assertEqual(public_ep['compute'][0]['region'], 'North')
        self.assertEqual(public_ep['compute'][0]['url'],
                         "https://compute.north.host/novapi/public")

    def test_service_catalog_alias_find_official(self):
        auth_ref = access.create(auth_token=uuid.uuid4().hex,
                                 body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        # Tests that we find the block-storage endpoint when we request
        # the volume endpoint.
        public_ep = sc.get_endpoints(service_type='volume',
                                     interface='public',
                                     region_name='North')
        self.assertEqual(public_ep['block-storage'][0]['region'], 'North')
        self.assertEqual(public_ep['block-storage'][0]['url'],
                         "http://cinder.north.host/cinderapi/public")

    def test_service_catalog_alias_find_exact_match(self):
        auth_ref = access.create(auth_token=uuid.uuid4().hex,
                                 body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        # Tests that we find the volumev3 endpoint when we request it.
        public_ep = sc.get_endpoints(service_type='volumev3',
                                     interface='public')
        self.assertEqual(public_ep['volumev3'][0]['region'], 'South')
        self.assertEqual(public_ep['volumev3'][0]['url'],
                         "http://cinder.south.host/cinderapi/public/v3")

    def test_service_catalog_alias_find_best_match(self):
        auth_ref = access.create(auth_token=uuid.uuid4().hex,
                                 body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        # Tests that we find the volumev3 endpoint when we request
        # block-storage when only volumev2 and volumev3 are present since
        # volumev3 comes first in the list.
        public_ep = sc.get_endpoints(service_type='block-storage',
                                     interface='public',
                                     region_name='South')
        self.assertEqual(public_ep['volumev3'][0]['region'], 'South')
        self.assertEqual(public_ep['volumev3'][0]['url'],
                         "http://cinder.south.host/cinderapi/public/v3")

    def test_service_catalog_alias_all_by_name(self):
        auth_ref = access.create(auth_token=uuid.uuid4().hex,
                                 body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        # Tests that we find all the cinder endpoints since we request
        # them by name and that no filtering related to aliases happens.
        public_ep = sc.get_endpoints(service_name='cinder',
                                     interface='public')
        self.assertEqual(public_ep['volumev2'][0]['region'], 'South')
        self.assertEqual(public_ep['volumev2'][0]['url'],
                         "http://cinder.south.host/cinderapi/public/v2")
        self.assertEqual(public_ep['volumev3'][0]['region'], 'South')
        self.assertEqual(public_ep['volumev3'][0]['url'],
                         "http://cinder.south.host/cinderapi/public/v3")
        self.assertEqual(public_ep['block-storage'][0]['region'], 'North')
        self.assertEqual(public_ep['block-storage'][0]['url'],
                         "http://cinder.north.host/cinderapi/public")

    def test_service_catalog_regions(self):
        self.AUTH_RESPONSE_BODY['token']['region_name'] = "North"
        auth_ref = access.create(auth_token=uuid.uuid4().hex,
                                 body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        url = sc.url_for(service_type='image', interface='public')
        self.assertEqual(url, "http://glance.north.host/glanceapi/public")

        self.AUTH_RESPONSE_BODY['token']['region_name'] = "South"
        auth_ref = access.create(auth_token=uuid.uuid4().hex,
                                 body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog
        url = sc.url_for(service_type='image',
                         region_name="South",
                         interface='internal')
        self.assertEqual(url, "http://glance.south.host/glanceapi/internal")

    def test_service_catalog_empty(self):
        self.AUTH_RESPONSE_BODY['token']['catalog'] = []
        auth_ref = access.create(auth_token=uuid.uuid4().hex,
                                 body=self.AUTH_RESPONSE_BODY)
        self.assertRaises(exceptions.EmptyCatalog,
                          auth_ref.service_catalog.url_for,
                          service_type='image',
                          interface='internalURL')

    def test_service_catalog_get_endpoints_region_names(self):
        sc = access.create(auth_token=uuid.uuid4().hex,
                           body=self.AUTH_RESPONSE_BODY).service_catalog

        endpoints = sc.get_endpoints(service_type='image', region_name='North')
        self.assertEqual(len(endpoints), 1)
        for endpoint in endpoints['image']:
            self.assertEqual(endpoint['url'],
                             self.north_endpoints[endpoint['interface']])

        endpoints = sc.get_endpoints(service_type='image', region_name='South')
        self.assertEqual(len(endpoints), 1)
        for endpoint in endpoints['image']:
            self.assertEqual(endpoint['url'],
                             self.south_endpoints[endpoint['interface']])

        endpoints = sc.get_endpoints(service_type='compute')
        self.assertEqual(len(endpoints['compute']), 3)

        endpoints = sc.get_endpoints(service_type='compute',
                                     region_name='North')
        self.assertEqual(len(endpoints['compute']), 3)

        endpoints = sc.get_endpoints(service_type='compute',
                                     region_name='West')
        self.assertEqual(len(endpoints['compute']), 0)

    def test_service_catalog_url_for_region_names(self):
        sc = access.create(auth_token=uuid.uuid4().hex,
                           body=self.AUTH_RESPONSE_BODY).service_catalog

        url = sc.url_for(service_type='image', region_name='North')
        self.assertEqual(url, self.north_endpoints['public'])

        url = sc.url_for(service_type='image', region_name='South')
        self.assertEqual(url, self.south_endpoints['public'])

        self.assertRaises(exceptions.EndpointNotFound, sc.url_for,
                          service_type='image', region_name='West')

    def test_service_catalog_get_url_region_names(self):
        sc = access.create(auth_token=uuid.uuid4().hex,
                           body=self.AUTH_RESPONSE_BODY).service_catalog

        urls = sc.get_urls(service_type='image')
        self.assertEqual(len(urls), 2)

        urls = sc.get_urls(service_type='image', region_name='North')
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], self.north_endpoints['public'])

        urls = sc.get_urls(service_type='image', region_name='South')
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], self.south_endpoints['public'])

        urls = sc.get_urls(service_type='image', region_name='West')
        self.assertEqual(len(urls), 0)

    def test_service_catalog_service_name(self):
        sc = access.create(auth_token=uuid.uuid4().hex,
                           body=self.AUTH_RESPONSE_BODY).service_catalog

        url = sc.url_for(service_name='glance', interface='public',
                         service_type='image', region_name='North')
        self.assertEqual('http://glance.north.host/glanceapi/public', url)

        url = sc.url_for(service_name='glance', interface='public',
                         service_type='image', region_name='South')
        self.assertEqual('http://glance.south.host/glanceapi/public', url)

        self.assertRaises(exceptions.EndpointNotFound, sc.url_for,
                          service_name='glance', service_type='compute')

        urls = sc.get_urls(service_type='image', service_name='glance',
                           interface='public')

        self.assertIn('http://glance.north.host/glanceapi/public', urls)
        self.assertIn('http://glance.south.host/glanceapi/public', urls)

        urls = sc.get_urls(service_type='image',
                           service_name='Servers',
                           interface='public')

        self.assertEqual(0, len(urls))

    def test_service_catalog_without_name(self):
        f = fixture.V3Token(audit_chain_id=uuid.uuid4().hex)

        if not f.project_id:
            f.set_project_scope()

        f.add_role(name='admin')
        f.add_role(name='member')

        region = 'RegionOne'
        tenant = '225da22d3ce34b15877ea70b2a575f58'

        s = f.add_service('volume')
        s.add_standard_endpoints(
            public='http://public.com:8776/v1/%s' % tenant,
            internal='http://internal:8776/v1/%s' % tenant,
            admin='http://admin:8776/v1/%s' % tenant,
            region=region)

        s = f.add_service('image')
        s.add_standard_endpoints(public='http://public.com:9292/v1',
                                 internal='http://internal:9292/v1',
                                 admin='http://admin:9292/v1',
                                 region=region)

        s = f.add_service('compute')
        s.add_standard_endpoints(
            public='http://public.com:8774/v2/%s' % tenant,
            internal='http://internal:8774/v2/%s' % tenant,
            admin='http://admin:8774/v2/%s' % tenant,
            region=region)

        s = f.add_service('ec2')
        s.add_standard_endpoints(
            public='http://public.com:8773/services/Cloud',
            internal='http://internal:8773/services/Cloud',
            admin='http://admin:8773/services/Admin',
            region=region)

        s = f.add_service('identity')
        s.add_standard_endpoints(public='http://public.com:5000/v3',
                                 internal='http://internal:5000/v3',
                                 admin='http://admin:35357/v3',
                                 region=region)

        pr_auth_ref = access.create(body=f)
        pr_sc = pr_auth_ref.service_catalog

        # this will work because there are no service names on that token
        url_ref = 'http://public.com:8774/v2/225da22d3ce34b15877ea70b2a575f58'
        url = pr_sc.url_for(service_type='compute', service_name='NotExist',
                            interface='public')
        self.assertEqual(url_ref, url)

        ab_auth_ref = access.create(body=self.AUTH_RESPONSE_BODY)
        ab_sc = ab_auth_ref.service_catalog

        # this won't work because there is a name and it's not this one
        self.assertRaises(exceptions.EndpointNotFound, ab_sc.url_for,
                          service_type='compute', service_name='NotExist',
                          interface='public')


class ServiceCatalogV3Test(ServiceCatalogTest):

    def test_building_a_service_catalog(self):
        sc = access.create(auth_token=uuid.uuid4().hex,
                           body=self.AUTH_RESPONSE_BODY).service_catalog

        self.assertEqual(sc.url_for(service_type='compute'),
                         'https://compute.north.host/novapi/public')
        self.assertEqual(sc.url_for(service_type='compute',
                                    interface='internal'),
                         'https://compute.north.host/novapi/internal')

        self.assertRaises(exceptions.EndpointNotFound,
                          sc.url_for,
                          region_name='South',
                          service_type='compute')

    def test_service_catalog_endpoints(self):
        sc = access.create(auth_token=uuid.uuid4().hex,
                           body=self.AUTH_RESPONSE_BODY).service_catalog

        public_ep = sc.get_endpoints(service_type='compute',
                                     interface='public')
        self.assertEqual(public_ep['compute'][0]['region_id'], 'North')
        self.assertEqual(public_ep['compute'][0]['url'],
                         'https://compute.north.host/novapi/public')

    def test_service_catalog_multiple_service_types(self):
        token = fixture.V3Token()
        token.set_project_scope()

        for i in range(3):
            s = token.add_service('compute')
            s.add_standard_endpoints(public='public-%d' % i,
                                     admin='admin-%d' % i,
                                     internal='internal-%d' % i,
                                     region='region-%d' % i)

        auth_ref = access.create(resp=None, body=token)

        urls = auth_ref.service_catalog.get_urls(service_type='compute',
                                                 interface='public')

        self.assertEqual(set(['public-0', 'public-1', 'public-2']), set(urls))

        urls = auth_ref.service_catalog.get_urls(service_type='compute',
                                                 interface='public',
                                                 region_name='region-1')

        self.assertEqual(('public-1', ), urls)

    def test_service_catalog_endpoint_id(self):
        token = fixture.V3Token()
        token.set_project_scope()

        service_id = uuid.uuid4().hex
        endpoint_id = uuid.uuid4().hex
        public_url = uuid.uuid4().hex

        s = token.add_service('compute', id=service_id)
        s.add_endpoint('public', public_url, id=endpoint_id)
        s.add_endpoint('public', uuid.uuid4().hex)

        auth_ref = access.create(body=token)

        # initially assert that we get back all our urls for a simple filter
        urls = auth_ref.service_catalog.get_urls(service_type='compute',
                                                 interface='public')
        self.assertEqual(2, len(urls))

        # with bad endpoint_id nothing should be found
        urls = auth_ref.service_catalog.get_urls(service_type='compute',
                                                 endpoint_id=uuid.uuid4().hex,
                                                 interface='public')

        self.assertEqual(0, len(urls))

        # with service_id we get back both public endpoints
        urls = auth_ref.service_catalog.get_urls(service_type='compute',
                                                 service_id=service_id,
                                                 interface='public')
        self.assertEqual(2, len(urls))

        # with service_id and endpoint_id we get back the url we want
        urls = auth_ref.service_catalog.get_urls(service_type='compute',
                                                 service_id=service_id,
                                                 endpoint_id=endpoint_id,
                                                 interface='public')

        self.assertEqual((public_url, ), urls)

        # with service_id and endpoint_id we get back the url we want
        urls = auth_ref.service_catalog.get_urls(service_type='compute',
                                                 endpoint_id=endpoint_id,
                                                 interface='public')

        self.assertEqual((public_url, ), urls)

    def test_service_catalog_without_service_type(self):
        token = fixture.V3Token()
        token.set_project_scope()

        public_urls = []

        for i in range(0, 3):
            public_url = uuid.uuid4().hex
            public_urls.append(public_url)

            s = token.add_service(uuid.uuid4().hex)
            s.add_endpoint('public', public_url)

        auth_ref = access.create(body=token)
        urls = auth_ref.service_catalog.get_urls(interface='public')

        self.assertEqual(3, len(urls))

        for p in public_urls:
            self.assertIn(p, urls)
