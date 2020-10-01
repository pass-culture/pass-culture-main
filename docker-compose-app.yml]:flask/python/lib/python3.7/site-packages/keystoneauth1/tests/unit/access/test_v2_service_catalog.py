#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import uuid

from keystoneauth1 import access
from keystoneauth1 import exceptions
from keystoneauth1 import fixture
from keystoneauth1.tests.unit import utils


class ServiceCatalogTest(utils.TestCase):
    def setUp(self):
        super(ServiceCatalogTest, self).setUp()

        self.AUTH_RESPONSE_BODY = fixture.V2Token(
            token_id='ab48a9efdfedb23ty3494',
            expires='2010-11-01T03:32:15-05:00',
            tenant_id='345',
            tenant_name='My Project',
            user_id='123',
            user_name='jqsmith',
            audit_chain_id=uuid.uuid4().hex)

        self.AUTH_RESPONSE_BODY.add_role(id='234', name='compute:admin')
        role = self.AUTH_RESPONSE_BODY.add_role(id='235',
                                                name='object-store:admin')
        role['tenantId'] = '1'

        s = self.AUTH_RESPONSE_BODY.add_service('compute', 'Cloud Servers')
        endpoint = s.add_endpoint(
            public='https://compute.north.host/v1/1234',
            internal='https://compute.north.host/v1/1234',
            region='North')
        endpoint['tenantId'] = '1'
        endpoint['versionId'] = '1.0'
        endpoint['versionInfo'] = 'https://compute.north.host/v1.0/'
        endpoint['versionList'] = 'https://compute.north.host/'

        endpoint = s.add_endpoint(
            public='https://compute.north.host/v1.1/3456',
            internal='https://compute.north.host/v1.1/3456',
            region='North')
        endpoint['tenantId'] = '2'
        endpoint['versionId'] = '1.1'
        endpoint['versionInfo'] = 'https://compute.north.host/v1.1/'
        endpoint['versionList'] = 'https://compute.north.host/'

        s = self.AUTH_RESPONSE_BODY.add_service('object-store', 'Cloud Files')
        endpoint = s.add_endpoint(public='https://swift.north.host/v1/blah',
                                  internal='https://swift.north.host/v1/blah',
                                  region='South')
        endpoint['tenantId'] = '11'
        endpoint['versionId'] = '1.0'
        endpoint['versionInfo'] = 'uri'
        endpoint['versionList'] = 'uri'

        endpoint = s.add_endpoint(
            public='https://swift.north.host/v1.1/blah',
            internal='https://compute.north.host/v1.1/blah',
            region='South')
        endpoint['tenantId'] = '2'
        endpoint['versionId'] = '1.1'
        endpoint['versionInfo'] = 'https://swift.north.host/v1.1/'
        endpoint['versionList'] = 'https://swift.north.host/'

        s = self.AUTH_RESPONSE_BODY.add_service('image', 'Image Servers')
        s.add_endpoint(public='https://image.north.host/v1/',
                       internal='https://image-internal.north.host/v1/',
                       region='North')
        s.add_endpoint(public='https://image.south.host/v1/',
                       internal='https://image-internal.south.host/v1/',
                       region='South')

    def test_building_a_service_catalog(self):
        auth_ref = access.create(body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        self.assertEqual(sc.url_for(service_type='compute'),
                         "https://compute.north.host/v1/1234")
        self.assertRaises(exceptions.EndpointNotFound,
                          sc.url_for,
                          region_name="South",
                          service_type='compute')

    def test_service_catalog_endpoints(self):
        auth_ref = access.create(body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog
        public_ep = sc.get_endpoints(service_type='compute',
                                     interface='publicURL')
        self.assertEqual(public_ep['compute'][1]['tenantId'], '2')
        self.assertEqual(public_ep['compute'][1]['versionId'], '1.1')
        self.assertEqual(public_ep['compute'][1]['internalURL'],
                         "https://compute.north.host/v1.1/3456")

    def test_service_catalog_empty(self):
        self.AUTH_RESPONSE_BODY['access']['serviceCatalog'] = []
        auth_ref = access.create(body=self.AUTH_RESPONSE_BODY)
        self.assertRaises(exceptions.EmptyCatalog,
                          auth_ref.service_catalog.url_for,
                          service_type='image',
                          interface='internalURL')

    def test_service_catalog_get_endpoints_region_names(self):
        auth_ref = access.create(body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        endpoints = sc.get_endpoints(service_type='image', region_name='North')
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints['image'][0]['publicURL'],
                         'https://image.north.host/v1/')

        endpoints = sc.get_endpoints(service_type='image', region_name='South')
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints['image'][0]['publicURL'],
                         'https://image.south.host/v1/')

        endpoints = sc.get_endpoints(service_type='compute')
        self.assertEqual(len(endpoints['compute']), 2)

        endpoints = sc.get_endpoints(service_type='compute',
                                     region_name='North')
        self.assertEqual(len(endpoints['compute']), 2)

        endpoints = sc.get_endpoints(service_type='compute',
                                     region_name='West')
        self.assertEqual(len(endpoints['compute']), 0)

    def test_service_catalog_url_for_region_names(self):
        auth_ref = access.create(body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        url = sc.url_for(service_type='image', region_name='North')
        self.assertEqual(url, 'https://image.north.host/v1/')

        url = sc.url_for(service_type='image', region_name='South')
        self.assertEqual(url, 'https://image.south.host/v1/')

        self.assertRaises(exceptions.EndpointNotFound, sc.url_for,
                          service_type='image', region_name='West')

    def test_servcie_catalog_get_url_region_names(self):
        auth_ref = access.create(body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        urls = sc.get_urls(service_type='image')
        self.assertEqual(len(urls), 2)

        urls = sc.get_urls(service_type='image', region_name='North')
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], 'https://image.north.host/v1/')

        urls = sc.get_urls(service_type='image', region_name='South')
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], 'https://image.south.host/v1/')

        urls = sc.get_urls(service_type='image', region_name='West')
        self.assertEqual(len(urls), 0)

    def test_service_catalog_service_name(self):
        auth_ref = access.create(body=self.AUTH_RESPONSE_BODY)
        sc = auth_ref.service_catalog

        url = sc.url_for(service_name='Image Servers', interface='public',
                         service_type='image', region_name='North')
        self.assertEqual('https://image.north.host/v1/', url)

        self.assertRaises(exceptions.EndpointNotFound, sc.url_for,
                          service_name='Image Servers', service_type='compute')

        urls = sc.get_urls(service_type='image', service_name='Image Servers',
                           interface='public')

        self.assertIn('https://image.north.host/v1/', urls)
        self.assertIn('https://image.south.host/v1/', urls)

        urls = sc.get_urls(service_type='image', service_name='Servers',
                           interface='public')

        self.assertEqual(0, len(urls))

    def test_service_catalog_multiple_service_types(self):
        token = fixture.V2Token()
        token.set_scope()

        for i in range(3):
            s = token.add_service('compute')
            s.add_endpoint(public='public-%d' % i,
                           admin='admin-%d' % i,
                           internal='internal-%d' % i,
                           region='region-%d' % i)

        auth_ref = access.create(body=token)

        urls = auth_ref.service_catalog.get_urls(service_type='compute',
                                                 interface='publicURL')

        self.assertEqual(set(['public-0', 'public-1', 'public-2']), set(urls))

        urls = auth_ref.service_catalog.get_urls(service_type='compute',
                                                 interface='publicURL',
                                                 region_name='region-1')

        self.assertEqual(('public-1', ), urls)

    def test_service_catalog_endpoint_id(self):
        token = fixture.V2Token()
        token.set_scope()
        endpoint_id = uuid.uuid4().hex
        public_url = uuid.uuid4().hex

        s = token.add_service('compute')
        s.add_endpoint(public=public_url, id=endpoint_id)
        s.add_endpoint(public=uuid.uuid4().hex)

        auth_ref = access.create(body=token)

        # initially assert that we get back all our urls for a simple filter
        urls = auth_ref.service_catalog.get_urls(interface='public')
        self.assertEqual(2, len(urls))

        urls = auth_ref.service_catalog.get_urls(endpoint_id=endpoint_id,
                                                 interface='public')

        self.assertEqual((public_url, ), urls)

        # with bad endpoint_id nothing should be found
        urls = auth_ref.service_catalog.get_urls(endpoint_id=uuid.uuid4().hex,
                                                 interface='public')

        self.assertEqual(0, len(urls))

        # we ignore a service_id because v2 doesn't know what it is
        urls = auth_ref.service_catalog.get_urls(endpoint_id=endpoint_id,
                                                 service_id=uuid.uuid4().hex,
                                                 interface='public')

        self.assertEqual((public_url, ), urls)

    def test_service_catalog_without_service_type(self):
        token = fixture.V2Token()
        token.set_scope()

        public_urls = []

        for i in range(0, 3):
            public_url = uuid.uuid4().hex
            public_urls.append(public_url)

            s = token.add_service(uuid.uuid4().hex)
            s.add_endpoint(public=public_url)

        auth_ref = access.create(body=token)
        urls = auth_ref.service_catalog.get_urls(service_type=None,
                                                 interface='public')

        self.assertEqual(3, len(urls))

        for p in public_urls:
            self.assertIn(p, urls)
