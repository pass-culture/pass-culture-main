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

import abc
import collections
import uuid

import six
from six.moves import urllib

from keystoneauth1 import _utils
from keystoneauth1 import access
from keystoneauth1 import adapter
from keystoneauth1 import discover
from keystoneauth1 import exceptions
from keystoneauth1 import fixture
from keystoneauth1 import identity
from keystoneauth1 import plugin
from keystoneauth1 import session
from keystoneauth1.tests.unit import utils

_Endpoints = collections.namedtuple(
    'ServiceVersion',
    'public, internal, admin')

_ServiceVersion = collections.namedtuple(
    'ServiceVersion',
    'discovery, service')


class FakeServiceEndpoints(object):
    def __init__(self, base_url, versions=None, project_id=None, **kwargs):
        self.base_url = base_url
        self._interfaces = {}
        for interface in ('public', 'internal', 'admin'):
            if interface in kwargs and not kwargs[interface]:
                self._interfaces[interface] = False
            else:
                self._interfaces[interface] = True

        self.versions = {}
        self.unversioned = self._make_urls()
        if not versions:
            self.catalog = self.unversioned
        else:
            self.catalog = self._make_urls(versions[0], project_id)
            for version in versions:
                self.versions[version] = _ServiceVersion(
                    self._make_urls(version),
                    self._make_urls(version, project_id),
                )

    def _make_urls(self, *parts):
        return _Endpoints(
            self._make_url('public', *parts),
            self._make_url('internal', *parts),
            self._make_url('admin', *parts),
        )

    def _make_url(self, interface, *parts):
        if not self._interfaces[interface]:
            return None
        url = urllib.parse.urljoin(self.base_url + '/', interface)
        for part in parts:
            if part:
                url = urllib.parse.urljoin(url + '/', part)
        return url


@six.add_metaclass(abc.ABCMeta)
class CommonIdentityTests(object):

    PROJECT_ID = uuid.uuid4().hex
    TEST_ROOT_URL = 'http://127.0.0.1:5000/'
    TEST_ROOT_ADMIN_URL = 'http://127.0.0.1:35357/'

    TEST_COMPUTE_BASE = 'https://compute.example.com'
    TEST_COMPUTE_PUBLIC = TEST_COMPUTE_BASE + '/nova/public'
    TEST_COMPUTE_INTERNAL = TEST_COMPUTE_BASE + '/nova/internal'
    TEST_COMPUTE_ADMIN = TEST_COMPUTE_BASE + '/nova/admin'

    TEST_VOLUME = FakeServiceEndpoints(
        base_url='https://block-storage.example.com',
        versions=['v3', 'v2'], project_id=PROJECT_ID)

    TEST_BAREMETAL_BASE = 'https://baremetal.example.com'
    TEST_BAREMETAL_INTERNAL = TEST_BAREMETAL_BASE + '/internal'

    TEST_PASS = uuid.uuid4().hex

    def setUp(self):
        super(CommonIdentityTests, self).setUp()

        self.TEST_URL = '%s%s' % (self.TEST_ROOT_URL, self.version)
        self.TEST_ADMIN_URL = '%s%s' % (self.TEST_ROOT_ADMIN_URL, self.version)
        self.TEST_DISCOVERY = fixture.DiscoveryList(href=self.TEST_ROOT_URL)

        self.stub_auth_data()

    @abc.abstractmethod
    def create_auth_plugin(self, **kwargs):
        """Create an auth plugin that makes sense for the auth data.

        It doesn't really matter what auth mechanism is used but it should be
        appropriate to the API version.
        """

    @abc.abstractmethod
    def get_auth_data(self, **kwargs):
        """Return fake authentication data.

        This should register a valid token response and ensure that the compute
        endpoints are set to TEST_COMPUTE_PUBLIC, _INTERNAL and _ADMIN.
        """

    def stub_auth_data(self, **kwargs):
        token = self.get_auth_data(**kwargs)
        self.user_id = token.user_id

        try:
            self.project_id = token.project_id
        except AttributeError:
            self.project_id = token.tenant_id

        self.stub_auth(json=token)

    @abc.abstractproperty
    def version(self):
        """The API version being tested."""

    def test_discovering(self):
        disc = fixture.DiscoveryList(v2=False, v3=False)

        disc.add_nova_microversion(
            href=self.TEST_COMPUTE_ADMIN,
            id='v2.1', status='CURRENT',
            min_version='2.1', version='2.38')

        self.stub_url('GET', [],
                      base_url=self.TEST_COMPUTE_ADMIN,
                      json=disc)

        body = 'SUCCESS'

        # which gives our sample values
        self.stub_url('GET', ['path'],
                      text=body, base_url=self.TEST_COMPUTE_ADMIN)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        resp = s.get('/path', endpoint_filter={'service_type': 'compute',
                                               'interface': 'admin',
                                               'version': '2.1'})

        self.assertEqual(200, resp.status_code)
        self.assertEqual(body, resp.text)

        new_body = 'SC SUCCESS'
        # if we don't specify a version, we use the URL from the SC
        self.stub_url('GET', ['path'],
                      base_url=self.TEST_COMPUTE_ADMIN,
                      text=new_body)

        resp = s.get('/path', endpoint_filter={'service_type': 'compute',
                                               'interface': 'admin'})

        self.assertEqual(200, resp.status_code)
        self.assertEqual(new_body, resp.text)

    def test_discovery_uses_provided_session_cache(self):
        disc = fixture.DiscoveryList(v2=False, v3=False)

        disc.add_nova_microversion(
            href=self.TEST_COMPUTE_ADMIN,
            id='v2.1', status='CURRENT',
            min_version='2.1', version='2.38')

        # register responses such that if the discovery URL is hit more than
        # once then the response will be invalid and not point to COMPUTE_ADMIN
        resps = [{'json': disc}, {'status_code': 500}]
        self.requests_mock.get(self.TEST_COMPUTE_ADMIN, resps)

        body = 'SUCCESS'
        self.stub_url('GET', ['path'],
                      text=body, base_url=self.TEST_COMPUTE_ADMIN)

        cache = {}
        # now either of the two plugins I use, it should not cause a second
        # request to the discovery url.
        s = session.Session(discovery_cache=cache)
        a = self.create_auth_plugin()
        b = self.create_auth_plugin()

        for auth in (a, b):
            resp = s.get('/path',
                         auth=auth,
                         endpoint_filter={'service_type': 'compute',
                                          'interface': 'admin',
                                          'version': '2.1'})

            self.assertEqual(200, resp.status_code)
            self.assertEqual(body, resp.text)
        self.assertIn(self.TEST_COMPUTE_ADMIN, cache.keys())

    def test_discovery_uses_session_cache(self):
        disc = fixture.DiscoveryList(v2=False, v3=False)

        disc.add_nova_microversion(
            href=self.TEST_COMPUTE_ADMIN,
            id='v2.1', status='CURRENT',
            min_version='2.1', version='2.38')

        # register responses such that if the discovery URL is hit more than
        # once then the response will be invalid and not point to COMPUTE_ADMIN
        resps = [{'json': disc}, {'status_code': 500}]
        self.requests_mock.get(self.TEST_COMPUTE_ADMIN, resps)

        body = 'SUCCESS'
        self.stub_url('GET', ['path'],
                      base_url=self.TEST_COMPUTE_ADMIN,
                      text=body)

        filter = {'service_type': 'compute', 'interface': 'admin',
                  'version': '2.1'}

        # create a session and call the endpoint, causing its cache to be set
        sess = session.Session()
        sess.get('/path', auth=self.create_auth_plugin(),
                 endpoint_filter=filter)
        self.assertIn(self.TEST_COMPUTE_ADMIN, sess._discovery_cache.keys())

        # now either of the two plugins I use, it should not cause a second
        # request to the discovery url.
        a = self.create_auth_plugin()
        b = self.create_auth_plugin()

        for auth in (a, b):
            resp = sess.get('/path', auth=auth, endpoint_filter=filter)
            self.assertEqual(200, resp.status_code)
            self.assertEqual(body, resp.text)

    def test_discovery_uses_plugin_cache(self):
        disc = fixture.DiscoveryList(v2=False, v3=False)

        disc.add_nova_microversion(
            href=self.TEST_COMPUTE_ADMIN,
            id='v2.1', status='CURRENT',
            min_version='2.1', version='2.38')

        # register responses such that if the discovery URL is hit more than
        # once then the response will be invalid and not point to COMPUTE_ADMIN
        resps = [{'json': disc}, {'status_code': 500}]
        self.requests_mock.get(self.TEST_COMPUTE_ADMIN, resps)

        body = 'SUCCESS'
        self.stub_url('GET', ['path'],
                      base_url=self.TEST_COMPUTE_ADMIN,
                      text=body)

        # now either of the two sessions I use, it should not cause a second
        # request to the discovery url. Calling discovery directly should also
        # not cause an additional request.
        sa = session.Session()
        sb = session.Session()
        auth = self.create_auth_plugin()

        for sess in (sa, sb):
            resp = sess.get('/path',
                            auth=auth,
                            endpoint_filter={'service_type': 'compute',
                                             'interface': 'admin',
                                             'version': '2.1'})

            self.assertEqual(200, resp.status_code)
            self.assertEqual(body, resp.text)

    def test_discovery_uses_session_plugin_cache(self):
        disc = fixture.DiscoveryList(v2=False, v3=False)

        disc.add_nova_microversion(
            href=self.TEST_COMPUTE_ADMIN,
            id='v2.1', status='CURRENT',
            min_version='2.1', version='2.38')

        # register responses such that if the discovery URL is hit more than
        # once then the response will be invalid and not point to COMPUTE_ADMIN
        resps = [{'json': disc}, {'status_code': 500}]
        self.requests_mock.get(self.TEST_COMPUTE_ADMIN, resps)

        body = 'SUCCESS'
        self.stub_url('GET', ['path'],
                      base_url=self.TEST_COMPUTE_ADMIN,
                      text=body)

        filter = {'service_type': 'compute', 'interface': 'admin',
                  'version': '2.1'}

        # create a plugin and call the endpoint, causing its cache to be set
        plugin = self.create_auth_plugin()
        session.Session().get('/path', auth=plugin, endpoint_filter=filter)
        self.assertIn(self.TEST_COMPUTE_ADMIN, plugin._discovery_cache.keys())

        # with the plugin in the session, no more calls to the discovery URL
        sess = session.Session(auth=plugin)
        for auth in (plugin, self.create_auth_plugin()):
            resp = sess.get('/path', auth=auth, endpoint_filter=filter)
            self.assertEqual(200, resp.status_code)
            self.assertEqual(body, resp.text)

    def test_direct_discovery_provided_plugin_cache(self):
        # register responses such that if the discovery URL is hit more than
        # once then the response will be invalid and not point to COMPUTE_ADMIN
        resps = [{'json': self.TEST_DISCOVERY}, {'status_code': 500}]
        self.requests_mock.get(self.TEST_COMPUTE_ADMIN, resps)

        # now either of the two sessions I use, it should not cause a second
        # request to the discovery url. Calling discovery directly should also
        # not cause an additional request.
        sa = session.Session()
        sb = session.Session()
        discovery_cache = {}

        expected_url = self.TEST_COMPUTE_ADMIN + '/v2.0'
        for sess in (sa, sb):

            disc = discover.get_discovery(
                sess, self.TEST_COMPUTE_ADMIN, cache=discovery_cache)
            url = disc.url_for(('2', '0'))

            self.assertEqual(expected_url, url)

        self.assertIn(self.TEST_COMPUTE_ADMIN, discovery_cache.keys())

    def test_discovery_trailing_slash(self):
        # The discovery cache should treat root urls the same whether they have
        # a slash or not. If the url is called a second time (meaning the cache
        # didn't work, we'll hit the 500 error.
        self.requests_mock.get(
            'https://example.com', [
                {'json': self.TEST_DISCOVERY},
                {'status_code': 500}
            ])

        sess = session.Session()
        discovery_cache = {}

        expected_url = 'https://example.com/v2.0'

        for test_endpoint in ('https://example.com', 'https://example.com/'):
            disc = discover.get_discovery(
                sess, test_endpoint, cache=discovery_cache)
            url = disc.url_for(('2', '0'))

            self.assertEqual(expected_url, url)

        self.assertIn('https://example.com', discovery_cache.keys())
        self.assertNotIn('https://example.com/', discovery_cache.keys())

    def test_discovering_with_no_data(self):
        # which returns discovery information pointing to TEST_URL but there is
        # no data there.
        self.stub_url('GET', [],
                      base_url=self.TEST_COMPUTE_ADMIN,
                      status_code=400)

        # so the url that will be used is the same TEST_COMPUTE_ADMIN
        body = 'SUCCESS'
        self.stub_url('GET', ['path'], base_url=self.TEST_COMPUTE_ADMIN,
                      text=body, status_code=200)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        resp = s.get('/path', endpoint_filter={'service_type': 'compute',
                                               'interface': 'admin',
                                               'version': self.version})

        self.assertEqual(200, resp.status_code)
        self.assertEqual(body, resp.text)

    def test_direct_discovering_with_no_data(self):
        # returns discovery information pointing to TEST_URL but there is
        # no data there.
        self.stub_url('GET', [],
                      base_url=self.TEST_COMPUTE_ADMIN,
                      status_code=400)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        # A direct call for discovery should fail
        self.assertRaises(exceptions.BadRequest,
                          discover.get_discovery, s, self.TEST_COMPUTE_ADMIN)

    def test_discovering_with_relative_link(self):
        # need to construct list this way for relative
        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2('v2.0')
        disc.add_v3('v3')

        self.stub_url('GET', [], base_url=self.TEST_COMPUTE_ADMIN, json=disc)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        endpoint_v2 = s.get_endpoint(service_type='compute',
                                     interface='admin',
                                     version=(2, 0))

        endpoint_v3 = s.get_endpoint(service_type='compute',
                                     interface='admin',
                                     version=(3, 0))

        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v2.0', endpoint_v2)
        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v3', endpoint_v3)

    def test_direct_discovering(self):
        v2_compute = self.TEST_COMPUTE_ADMIN + '/v2.0'
        v3_compute = self.TEST_COMPUTE_ADMIN + '/v3'

        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2(v2_compute)
        disc.add_v3(v3_compute)

        self.stub_url('GET', [], base_url=self.TEST_COMPUTE_ADMIN, json=disc)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        catalog_url = s.get_endpoint(
            service_type='compute', interface='admin')
        disc = discover.get_discovery(s, catalog_url)

        url_v2 = disc.url_for(('2', '0'))
        url_v3 = disc.url_for(('3', '0'))

        self.assertEqual(v2_compute, url_v2)
        self.assertEqual(v3_compute, url_v3)

        # Verify that passing strings and not tuples works
        url_v2 = disc.url_for('2.0')
        url_v3 = disc.url_for('3.0')

        self.assertEqual(v2_compute, url_v2)
        self.assertEqual(v3_compute, url_v3)

    def test_discovering_version_no_discovery(self):

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        # Grab a version that can be returned without doing discovery
        # This tests that it doesn't make a discovery call because we don't
        # have a reqquest mock, and this will throw an exception if it tries
        version = s.get_api_major_version(
            service_type='volumev2', interface='admin')
        self.assertEqual((2, 0), version)

    def test_discovering_version_with_discovery(self):

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        v2_compute = self.TEST_COMPUTE_ADMIN + '/v2.0'
        v3_compute = self.TEST_COMPUTE_ADMIN + '/v3'

        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2(v2_compute)
        disc.add_v3(v3_compute)

        self.stub_url('GET', [], base_url=self.TEST_COMPUTE_ADMIN, json=disc)

        # This needs to do version discovery to find the version
        version = s.get_api_major_version(
            service_type='compute', interface='admin')
        self.assertEqual((3, 0), version)
        self.assertEqual(
            self.requests_mock.request_history[-1].url,
            self.TEST_COMPUTE_ADMIN)

    def test_direct_discovering_with_relative_link(self):
        # need to construct list this way for relative
        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2('v2.0')
        disc.add_v3('v3')

        self.stub_url('GET', [], base_url=self.TEST_COMPUTE_ADMIN, json=disc)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        catalog_url = s.get_endpoint(
            service_type='compute', interface='admin')
        disc = discover.get_discovery(s, catalog_url)

        url_v2 = disc.url_for(('2', '0'))
        url_v3 = disc.url_for(('3', '0'))

        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v2.0', url_v2)
        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v3', url_v3)

        # Verify that passing strings and not tuples works
        url_v2 = disc.url_for('2.0')
        url_v3 = disc.url_for('3.0')

        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v2.0', url_v2)
        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v3', url_v3)

    def test_discovering_with_relative_anchored_link(self):
        # need to construct list this way for relative
        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2('/v2.0')
        disc.add_v3('/v3')

        self.stub_url('GET', [], base_url=self.TEST_COMPUTE_ADMIN, json=disc)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        endpoint_v2 = s.get_endpoint(service_type='compute',
                                     interface='admin',
                                     version=(2, 0))

        endpoint_v3 = s.get_endpoint(service_type='compute',
                                     interface='admin',
                                     version=(3, 0))

        # by the nature of urljoin a relative link with a /path gets joined
        # back to the root.
        self.assertEqual(self.TEST_COMPUTE_BASE + '/v2.0', endpoint_v2)
        self.assertEqual(self.TEST_COMPUTE_BASE + '/v3', endpoint_v3)

    def test_discovering_with_protocol_relative(self):
        # strip up to and including the : leaving //host/path
        path = self.TEST_COMPUTE_ADMIN[self.TEST_COMPUTE_ADMIN.find(':') + 1:]

        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2(path + '/v2.0')
        disc.add_v3(path + '/v3')

        self.stub_url('GET', [], base_url=self.TEST_COMPUTE_ADMIN, json=disc)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        endpoint_v2 = s.get_endpoint(service_type='compute',
                                     interface='admin',
                                     version=(2, 0))

        endpoint_v3 = s.get_endpoint(service_type='compute',
                                     interface='admin',
                                     version=(3, 0))

        # ensures that the http is carried over from the lookup url
        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v2.0', endpoint_v2)
        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v3', endpoint_v3)

    def test_discovering_when_version_missing(self):
        # need to construct list this way for relative
        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2('v2.0')

        self.stub_url('GET', [], base_url=self.TEST_COMPUTE_ADMIN, json=disc)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        endpoint_v2 = s.get_endpoint(service_type='compute',
                                     interface='admin',
                                     version=(2, 0))

        endpoint_v3 = s.get_endpoint(service_type='compute',
                                     interface='admin',
                                     version=(3, 0))

        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v2.0', endpoint_v2)
        self.assertIsNone(endpoint_v3)

    def test_endpoint_data_no_version(self):
        path = self.TEST_COMPUTE_ADMIN[self.TEST_COMPUTE_ADMIN.find(':') + 1:]

        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2(path + '/v2.0')
        disc.add_v3(path + '/v3')

        self.stub_url('GET', [], base_url=self.TEST_COMPUTE_ADMIN, json=disc)
        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        data = a.get_endpoint_data(session=s,
                                   service_type='compute',
                                   interface='admin')

        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v3', data.url)
        # We should have gotten the version from the URL
        self.assertEqual((3, 0), data.api_version)

    def test_get_all_version_data_all_interfaces(self):

        for interface in ('public', 'internal', 'admin'):
            # The version discovery dict will not have a project_id
            disc = fixture.DiscoveryList(v2=False, v3=False)
            disc.add_nova_microversion(
                href=getattr(self.TEST_VOLUME.versions['v3'].discovery,
                             interface),
                id='v3.0', status='CURRENT',
                min_version='3.0', version='3.20')

            # Adding a v2 version to a service named volumev3 is not
            # an error. The service itself is cinder and has more than
            # one major version.
            disc.add_nova_microversion(
                href=getattr(self.TEST_VOLUME.versions['v2'].discovery,
                             interface),
                id='v2.0', status='SUPPORTED')

            self.stub_url(
                'GET', [],
                base_url=getattr(self.TEST_VOLUME.unversioned,
                                 interface) + '/',
                json=disc)

        for url in (
                self.TEST_COMPUTE_PUBLIC,
                self.TEST_COMPUTE_INTERNAL,
                self.TEST_COMPUTE_ADMIN):

            disc = fixture.DiscoveryList(v2=False, v3=False)
            disc.add_microversion(
                href=url, id='v2')
            disc.add_microversion(
                href=url, id='v2.1',
                min_version='2.1', max_version='2.35')

            self.stub_url('GET', [], base_url=url, json=disc)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        identity_endpoint = 'http://127.0.0.1:35357/{}/'.format(self.version)
        data = s.get_all_version_data(interface=None)
        self.assertEqual({
            'RegionOne': {
                'admin': {
                    'block-storage': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'SUPPORTED',
                        'status': 'SUPPORTED',
                        'url': 'https://block-storage.example.com/admin/v2',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '3.20',
                        'min_microversion': '3.0',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'CURRENT',
                        'status': 'CURRENT',
                        'url': 'https://block-storage.example.com/admin/v3',
                        'version': '3.0'
                    }],
                    'compute': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/admin',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '2.35',
                        'min_microversion': '2.1',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/admin',
                        'version': '2.1'}],
                    'identity': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': None,
                        'status': 'CURRENT',
                        'url': identity_endpoint,
                        'version': self.discovery_version,
                    }]
                },
                'internal': {
                    'baremetal': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': None,
                        'status': 'CURRENT',
                        'url': 'https://baremetal.example.com/internal/',
                        'version': None
                    }],
                    'block-storage': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'SUPPORTED',
                        'status': 'SUPPORTED',
                        'url': 'https://block-storage.example.com/internal/v2',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '3.20',
                        'min_microversion': '3.0',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'CURRENT',
                        'status': 'CURRENT',
                        'url': 'https://block-storage.example.com/internal/v3',
                        'version': '3.0'
                    }],
                    'compute': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/internal',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '2.35',
                        'min_microversion': '2.1',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/internal',
                        'version': '2.1'
                    }]
                },
                'public': {
                    'block-storage': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'SUPPORTED',
                        'status': 'SUPPORTED',
                        'url': 'https://block-storage.example.com/public/v2',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '3.20',
                        'min_microversion': '3.0',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'CURRENT',
                        'status': 'CURRENT',
                        'url': 'https://block-storage.example.com/public/v3',
                        'version': '3.0'
                    }],
                    'compute': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/public',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '2.35',
                        'min_microversion': '2.1',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/public',
                        'version': '2.1',
                    }]
                }
            }
        }, data)

    def test_get_all_version_data(self):

        cinder_disc = fixture.DiscoveryList(v2=False, v3=False)

        # The version discovery dict will not have a project_id
        cinder_disc.add_nova_microversion(
            href=self.TEST_VOLUME.versions['v3'].discovery.public,
            id='v3.0', status='CURRENT',
            min_version='3.0', version='3.20')

        # Adding a v2 version to a service named volumev3 is not
        # an error. The service itself is cinder and has more than
        # one major version.
        cinder_disc.add_nova_microversion(
            href=self.TEST_VOLUME.versions['v2'].discovery.public,
            id='v2.0', status='SUPPORTED')

        self.stub_url(
            'GET', [],
            base_url=self.TEST_VOLUME.unversioned.public + '/',
            json=cinder_disc)

        nova_disc = fixture.DiscoveryList(v2=False, v3=False)
        nova_disc.add_microversion(
            href=self.TEST_COMPUTE_PUBLIC, id='v2')
        nova_disc.add_microversion(
            href=self.TEST_COMPUTE_PUBLIC, id='v2.1',
            min_version='2.1', max_version='2.35')

        self.stub_url(
            'GET', [], base_url=self.TEST_COMPUTE_PUBLIC, json=nova_disc)
        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        data = s.get_all_version_data(interface='public')
        self.assertEqual({
            'RegionOne': {
                'public': {
                    'block-storage': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'SUPPORTED',
                        'status': 'SUPPORTED',
                        'url': 'https://block-storage.example.com/public/v2',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '3.20',
                        'min_microversion': '3.0',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'CURRENT',
                        'status': 'CURRENT',
                        'url': 'https://block-storage.example.com/public/v3',
                        'version': '3.0'
                    }],
                    'compute': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/public',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '2.35',
                        'min_microversion': '2.1',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/public',
                        'version': '2.1'
                    }],
                }
            }
        }, data)

    def test_get_all_version_data_by_service_type(self):
        nova_disc = fixture.DiscoveryList(v2=False, v3=False)
        nova_disc.add_microversion(
            href=self.TEST_COMPUTE_PUBLIC, id='v2')
        nova_disc.add_microversion(
            href=self.TEST_COMPUTE_PUBLIC, id='v2.1',
            min_version='2.1', max_version='2.35')

        self.stub_url(
            'GET', [], base_url=self.TEST_COMPUTE_PUBLIC, json=nova_disc)
        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        data = s.get_all_version_data(
            interface='public',
            service_type='compute')
        self.assertEqual({
            'RegionOne': {
                'public': {
                    'compute': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/public',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '2.35',
                        'min_microversion': '2.1',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/public',
                        'version': '2.1'
                    }],
                }
            }
        }, data)

    def test_get_all_version_data_adapter(self):
        nova_disc = fixture.DiscoveryList(v2=False, v3=False)
        nova_disc.add_microversion(
            href=self.TEST_COMPUTE_PUBLIC, id='v2')
        nova_disc.add_microversion(
            href=self.TEST_COMPUTE_PUBLIC, id='v2.1',
            min_version='2.1', max_version='2.35')

        self.stub_url(
            'GET', [], base_url=self.TEST_COMPUTE_PUBLIC, json=nova_disc)
        s = session.Session(auth=self.create_auth_plugin())
        a = adapter.Adapter(session=s, service_type='compute')

        data = a.get_all_version_data()
        self.assertEqual({
            'RegionOne': {
                'public': {
                    'compute': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/public',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '2.35',
                        'min_microversion': '2.1',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'stable',
                        'status': 'CURRENT',
                        'url': 'https://compute.example.com/nova/public',
                        'version': '2.1'
                    }],
                }
            }
        }, data)

    def test_get_all_version_data_service_alias(self):

        cinder_disc = fixture.DiscoveryList(v2=False, v3=False)

        # The version discovery dict will not have a project_id
        cinder_disc.add_nova_microversion(
            href=self.TEST_VOLUME.versions['v3'].discovery.public,
            id='v3.0', status='CURRENT',
            min_version='3.0', version='3.20')

        # Adding a v2 version to a service named volumev3 is not
        # an error. The service itself is cinder and has more than
        # one major version.
        cinder_disc.add_nova_microversion(
            href=self.TEST_VOLUME.versions['v2'].discovery.public,
            id='v2.0', status='SUPPORTED')

        self.stub_url(
            'GET', [],
            base_url=self.TEST_VOLUME.unversioned.public + '/',
            json=cinder_disc)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        data = s.get_all_version_data(
            interface='public',
            service_type='block-store')
        self.assertEqual({
            'RegionOne': {
                'public': {
                    'block-storage': [{
                        'collection': None,
                        'max_microversion': None,
                        'min_microversion': None,
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'SUPPORTED',
                        'status': 'SUPPORTED',
                        'url': 'https://block-storage.example.com/public/v2',
                        'version': '2.0'
                    }, {
                        'collection': None,
                        'max_microversion': '3.20',
                        'min_microversion': '3.0',
                        'next_min_version': None,
                        'not_before': None,
                        'raw_status': 'CURRENT',
                        'status': 'CURRENT',
                        'url': 'https://block-storage.example.com/public/v3',
                        'version': '3.0'
                    }],
                }
            }
        }, data)

    def test_endpoint_data_no_version_no_discovery(self):
        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        data = a.get_endpoint_data(session=s,
                                   service_type='compute',
                                   interface='admin',
                                   discover_versions=False)

        self.assertEqual(self.TEST_COMPUTE_ADMIN, data.url)
        # There's no version in the URL and no document - we have no idea
        self.assertIsNone(data.api_version)

    def test_endpoint_data_version_url_no_discovery(self):
        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        data = a.get_endpoint_data(session=s,
                                   service_type='volumev3',
                                   interface='admin',
                                   discover_versions=False)

        self.assertEqual(
            self.TEST_VOLUME.versions['v3'].service.admin, data.url)
        # There's v3 in the URL
        self.assertEqual((3, 0), data.api_version)

    def test_endpoint_no_version(self):
        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        data = a.get_endpoint(session=s,
                              service_type='compute',
                              interface='admin')

        self.assertEqual(self.TEST_COMPUTE_ADMIN, data)

    def test_endpoint_data_relative_version(self):
        # need to construct list this way for relative
        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2('v2.0')
        disc.add_v3('v3')

        self.stub_url('GET', [], base_url=self.TEST_COMPUTE_ADMIN, json=disc)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        data_v2 = a.get_endpoint_data(session=s,
                                      service_type='compute',
                                      interface='admin',
                                      min_version=(2, 0),
                                      max_version=(2, discover.LATEST))
        data_v3 = a.get_endpoint_data(session=s,
                                      service_type='compute',
                                      interface='admin',
                                      min_version=(3, 0),
                                      max_version=(3, discover.LATEST))

        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v2.0', data_v2.url)
        self.assertEqual(self.TEST_COMPUTE_ADMIN + '/v3', data_v3.url)

    def test_get_versioned_data(self):
        v2_compute = self.TEST_COMPUTE_ADMIN + '/v2.0'
        v3_compute = self.TEST_COMPUTE_ADMIN + '/v3'

        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2(v2_compute)
        disc.add_v3(v3_compute)

        # Make sure that we don't do more than one discovery call
        # register responses such that if the discovery URL is hit more than
        # once then the response will be invalid and not point to COMPUTE_ADMIN
        resps = [{'json': disc}, {'status_code': 500}]
        self.requests_mock.get(self.TEST_COMPUTE_ADMIN, resps)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        data = a.get_endpoint_data(session=s,
                                   service_type='compute',
                                   interface='admin')
        self.assertEqual(v3_compute, data.url)

        v2_data = data.get_versioned_data(s, min_version='2.0',
                                          max_version='2.latest')
        self.assertEqual(v2_compute, v2_data.url)
        self.assertEqual(v2_compute, v2_data.service_url)
        self.assertEqual(self.TEST_COMPUTE_ADMIN, v2_data.catalog_url)

        # Variants that all return v3 data
        for vkwargs in (dict(min_version='3.0', max_version='3.latest'),
                        # min/max spans major versions
                        dict(min_version='2.0', max_version='3.latest'),
                        # latest major max
                        dict(min_version='2.0', max_version='latest'),
                        # implicit max
                        dict(min_version='2.0'),
                        # implicit min/max
                        dict()):
            v3_data = data.get_versioned_data(s, **vkwargs)
            self.assertEqual(v3_compute, v3_data.url)
            self.assertEqual(v3_compute, v3_data.service_url)
            self.assertEqual(self.TEST_COMPUTE_ADMIN, v3_data.catalog_url)

    def test_get_current_versioned_data(self):
        v2_compute = self.TEST_COMPUTE_ADMIN + '/v2.0'
        v3_compute = self.TEST_COMPUTE_ADMIN + '/v3'

        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_v2(v2_compute)
        disc.add_v3(v3_compute)

        # Make sure that we don't do more than one discovery call
        # register responses such that if the discovery URL is hit more than
        # once then the response will be invalid and not point to COMPUTE_ADMIN
        resps = [{'json': disc}, {'status_code': 500}]
        self.requests_mock.get(self.TEST_COMPUTE_ADMIN, resps)

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        data = a.get_endpoint_data(session=s,
                                   service_type='compute',
                                   interface='admin')
        self.assertEqual(v3_compute, data.url)

        v3_data = data.get_current_versioned_data(s)

        self.assertEqual(v3_compute, v3_data.url)
        self.assertEqual(v3_compute, v3_data.service_url)
        self.assertEqual(self.TEST_COMPUTE_ADMIN, v3_data.catalog_url)
        self.assertEqual((3, 0), v3_data.api_version)
        self.assertIsNone(v3_data.min_microversion)
        self.assertIsNone(v3_data.max_microversion)

    def test_interface_list(self):

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        ep = s.get_endpoint(service_type='baremetal',
                            interface=['internal', 'public'])
        self.assertEqual(ep, self.TEST_BAREMETAL_INTERNAL)

        ep = s.get_endpoint(service_type='baremetal',
                            interface=['public', 'internal'])
        self.assertEqual(ep, self.TEST_BAREMETAL_INTERNAL)

        ep = s.get_endpoint(service_type='compute',
                            interface=['internal', 'public'])
        self.assertEqual(ep, self.TEST_COMPUTE_INTERNAL)

        ep = s.get_endpoint(service_type='compute',
                            interface=['public', 'internal'])
        self.assertEqual(ep, self.TEST_COMPUTE_PUBLIC)

    def test_get_versioned_data_volume_project_id(self):

        disc = fixture.DiscoveryList(v2=False, v3=False)

        # The version discovery dict will not have a project_id
        disc.add_nova_microversion(
            href=self.TEST_VOLUME.versions['v3'].discovery.public,
            id='v3.0', status='CURRENT',
            min_version='3.0', version='3.20')

        # Adding a v2 version to a service named volumev3 is not
        # an error. The service itself is cinder and has more than
        # one major version.
        disc.add_nova_microversion(
            href=self.TEST_VOLUME.versions['v2'].discovery.public,
            id='v2.0', status='SUPPORTED')

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        # volume endpoint ends in v3, we should not make an API call
        endpoint = a.get_endpoint(session=s,
                                  service_type='volumev3',
                                  interface='public',
                                  version='3.0')
        self.assertEqual(self.TEST_VOLUME.catalog.public, endpoint)

        resps = [{'json': disc}, {'status_code': 500}]

        # We should only try to fetch the versioned discovery url once
        self.requests_mock.get(
            self.TEST_VOLUME.versions['v3'].discovery.public + '/', resps)

        data = a.get_endpoint_data(session=s,
                                   service_type='volumev3',
                                   interface='public')
        self.assertEqual(self.TEST_VOLUME.versions['v3'].service.public,
                         data.url)

        v3_data = data.get_versioned_data(
            s, min_version='3.0', max_version='3.latest',
            project_id=self.project_id)

        self.assertEqual(self.TEST_VOLUME.versions['v3'].service.public,
                         v3_data.url)
        self.assertEqual(self.TEST_VOLUME.catalog.public, v3_data.catalog_url)
        self.assertEqual((3, 0), v3_data.min_microversion)
        self.assertEqual((3, 20), v3_data.max_microversion)
        self.assertEqual(self.TEST_VOLUME.versions['v3'].service.public,
                         v3_data.service_url)

        # Because of the v3 optimization before, requesting v2 should now go
        # find the unversioned endpoint
        self.requests_mock.get(self.TEST_VOLUME.unversioned.public, resps)
        v2_data = data.get_versioned_data(
            s, min_version='2.0', max_version='2.latest',
            project_id=self.project_id)

        # Even though we never requested volumev2 from the catalog, we should
        # wind up re-constructing it via version discovery and re-appending
        # the project_id to the URL
        self.assertEqual(self.TEST_VOLUME.versions['v2'].service.public,
                         v2_data.url)
        self.assertEqual(self.TEST_VOLUME.versions['v2'].service.public,
                         v2_data.service_url)
        self.assertEqual(self.TEST_VOLUME.catalog.public, v2_data.catalog_url)
        self.assertIsNone(v2_data.min_microversion)
        self.assertIsNone(v2_data.max_microversion)

    def test_get_versioned_data_volume_project_id_unversioned_first(self):

        disc = fixture.DiscoveryList(v2=False, v3=False)

        # The version discovery dict will not have a project_id
        disc.add_nova_microversion(
            href=self.TEST_VOLUME.versions['v3'].discovery.public,
            id='v3.0', status='CURRENT',
            min_version='3.0', version='3.20')

        # Adding a v2 version to a service named volumev3 is not
        # an error. The service itself is cinder and has more than
        # one major version.
        disc.add_nova_microversion(
            href=self.TEST_VOLUME.versions['v2'].discovery.public,
            id='v2.0', status='SUPPORTED')

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        # cinder endpoint ends in v3, we should not make an API call
        endpoint = a.get_endpoint(session=s,
                                  service_type='volumev3',
                                  interface='public',
                                  version='3.0')
        self.assertEqual(self.TEST_VOLUME.catalog.public, endpoint)

        resps = [{'json': disc}, {'status_code': 500}]

        # We should only try to fetch the unversioned non-project_id url once
        # Because the catalog has the versioned endpoint but we constructed
        # an unversioned endpoint, the url needs to have a trailing /
        self.requests_mock.get(
            self.TEST_VOLUME.unversioned.public + '/', resps)

        # Fetch v2.0 first - since that doesn't match endpoint optimization,
        # it should fetch the unversioned endpoint
        v2_data = s.get_endpoint_data(service_type='block-storage',
                                      interface='public',
                                      min_version='2.0',
                                      max_version='2.latest',
                                      project_id=self.project_id)

        # Even though we never requested volumev2 from the catalog, we should
        # wind up re-constructing it via version discovery and re-appending
        # the project_id to the URL
        self.assertEqual(self.TEST_VOLUME.versions['v2'].service.public,
                         v2_data.url)
        self.assertEqual(self.TEST_VOLUME.versions['v2'].service.public,
                         v2_data.service_url)
        self.assertEqual(self.TEST_VOLUME.catalog.public, v2_data.catalog_url)
        self.assertIsNone(v2_data.min_microversion)
        self.assertIsNone(v2_data.max_microversion)

        # Since we fetched from the unversioned endpoint to satisfy the
        # request for v2, we should have all the relevant data cached in the
        # discovery object - and should not fetch anything new.
        v3_data = v2_data.get_versioned_data(
            s, min_version='3.0', max_version='3.latest',
            project_id=self.project_id)

        self.assertEqual(self.TEST_VOLUME.versions['v3'].service.public,
                         v3_data.url)
        self.assertEqual(self.TEST_VOLUME.catalog.public, v3_data.catalog_url)
        self.assertEqual((3, 0), v3_data.min_microversion)
        self.assertEqual((3, 20), v3_data.max_microversion)
        self.assertEqual(self.TEST_VOLUME.versions['v3'].service.public,
                         v3_data.service_url)

    def test_trailing_slash_on_computed_endpoint(self):

        disc = fixture.DiscoveryList(v2=False, v3=False)

        # A versioned URL in the Catalog
        disc.add_nova_microversion(
            href=self.TEST_VOLUME.versions['v3'].discovery.public,
            id='v3.0', status='CURRENT',
            min_version='3.0', version='3.20')

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        # endpoint ends in v3, we will construct the unversioned endpoint.
        # Because the catalog has the versioned endpoint but we constructed
        # an unversioned endpoint, the url needs to have a trailing /
        self.requests_mock.get(
            self.TEST_VOLUME.unversioned.public + '/', json=disc)

        # We're requesting version 2 of block-storage to make sure we
        # trigger the logic constructing the unversioned endpoint from the
        # versioned endpoint in the catalog
        s.get_endpoint_data(service_type='block-storage',
                            interface='public',
                            min_version='2.0',
                            max_version='2.latest',
                            project_id=self.project_id)

        self.assertTrue(
            self.requests_mock.request_history[-1].url.endswith('/'))

    def test_no_trailing_slash_on_catalog_endpoint(self):

        disc = fixture.DiscoveryList(v2=False, v3=False)

        # A versioned URL in the Catalog
        disc.add_nova_microversion(
            href=self.TEST_COMPUTE_PUBLIC,
            id='v2.1', status='CURRENT',
            min_version='2.1', version='2.38')

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        # nova has unversioned endpoint in this catalog. We should not
        # modify it.
        self.requests_mock.get(self.TEST_COMPUTE_PUBLIC, json=disc)

        s.get_endpoint_data(service_type='compute',
                            interface='public',
                            min_version='2.1',
                            max_version='2.latest')

        self.assertFalse(
            self.requests_mock.request_history[-1].url.endswith('/'))

    def test_broken_discovery_endpoint(self):

        # Discovery document with a bogus/broken base URL
        disc = fixture.DiscoveryList(v2=False, v3=False)
        disc.add_nova_microversion(
            href='http://internal.example.com',
            id='v2.1', status='CURRENT',
            min_version='2.1', version='2.38')

        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        self.requests_mock.get(self.TEST_COMPUTE_PUBLIC, json=disc)

        data = s.get_endpoint_data(service_type='compute',
                                   interface='public',
                                   min_version='2.1',
                                   max_version='2.latest')

        # Verify that we get the versioned url based on the catalog url
        self.assertTrue(data.url, self.TEST_COMPUTE_PUBLIC + '/v2.1')

    def test_asking_for_auth_endpoint_ignores_checks(self):
        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        auth_url = s.get_endpoint(service_type='compute',
                                  interface=plugin.AUTH_INTERFACE)

        self.assertEqual(self.TEST_URL, auth_url)

    def _create_expired_auth_plugin(self, **kwargs):
        expires = _utils.before_utcnow(minutes=20)
        expired_token = self.get_auth_data(expires=expires)
        expired_auth_ref = access.create(body=expired_token)

        a = self.create_auth_plugin(**kwargs)
        a.auth_ref = expired_auth_ref
        return a

    def test_reauthenticate(self):
        a = self._create_expired_auth_plugin()
        expired_auth_ref = a.auth_ref
        s = session.Session(auth=a)
        self.assertIsNot(expired_auth_ref, a.get_access(s))

    def test_no_reauthenticate(self):
        a = self._create_expired_auth_plugin(reauthenticate=False)
        expired_auth_ref = a.auth_ref
        s = session.Session(auth=a)
        self.assertIs(expired_auth_ref, a.get_access(s))

    def test_invalidate(self):
        a = self.create_auth_plugin()
        s = session.Session(auth=a)

        # trigger token fetching
        s.get_auth_headers()

        self.assertTrue(a.auth_ref)
        self.assertTrue(a.invalidate())
        self.assertIsNone(a.auth_ref)
        self.assertFalse(a.invalidate())

    def test_get_auth_properties(self):
        a = self.create_auth_plugin()
        s = session.Session()

        self.assertEqual(self.user_id, a.get_user_id(s))
        self.assertEqual(self.project_id, a.get_project_id(s))

    def assertAccessInfoEqual(self, a, b):
        self.assertEqual(a.auth_token, b.auth_token)
        self.assertEqual(a._data, b._data)

    def test_check_cache_id_match(self):
        a = self.create_auth_plugin()
        b = self.create_auth_plugin()

        self.assertIsNot(a, b)
        self.assertIsNone(a.get_auth_state())
        self.assertIsNone(b.get_auth_state())

        a_id = a.get_cache_id()
        b_id = b.get_cache_id()

        self.assertIsNotNone(a_id)
        self.assertIsNotNone(b_id)

        self.assertEqual(a_id, b_id)

    def test_check_cache_id_no_match(self):
        a = self.create_auth_plugin(project_id='a')
        b = self.create_auth_plugin(project_id='b')

        self.assertIsNot(a, b)
        self.assertIsNone(a.get_auth_state())
        self.assertIsNone(b.get_auth_state())

        a_id = a.get_cache_id()
        b_id = b.get_cache_id()

        self.assertIsNotNone(a_id)
        self.assertIsNotNone(b_id)

        self.assertNotEqual(a_id, b_id)

    def test_get_set_auth_state(self):
        a = self.create_auth_plugin()
        b = self.create_auth_plugin()

        self.assertEqual(a.get_cache_id(), b.get_cache_id())

        s = session.Session()

        a_token = a.get_token(s)

        self.assertEqual(1, self.requests_mock.call_count)

        auth_state = a.get_auth_state()

        self.assertIsNotNone(auth_state)

        b.set_auth_state(auth_state)

        b_token = b.get_token(s)
        self.assertEqual(1, self.requests_mock.call_count)

        self.assertEqual(a_token, b_token)
        self.assertAccessInfoEqual(a.auth_ref, b.auth_ref)

    def test_pathless_url(self):
        disc = fixture.DiscoveryList(v2=False, v3=False)
        url = 'http://path.less.url:1234'
        disc.add_microversion(href=url, id='v2.1')

        self.stub_url('GET', base_url=url, status_code=200, json=disc)

        token = fixture.V2Token()
        service = token.add_service('network')
        service.add_endpoint(public=url, admin=url, internal=url)

        self.stub_url('POST', ['tokens'], base_url=url, json=token)

        v2_auth = identity.V2Password(url, username='u', password='p')

        sess = session.Session(auth=v2_auth)

        data = sess.get_endpoint_data(service_type='network')

        # Discovery ran and returned the URL and its version
        self.assertEqual(url, data.url)
        self.assertEqual((2, 1), data.api_version)

        # Run with a project_id to ensure that path is covered
        self.assertEqual(
            3, len(list(data._get_discovery_url_choices(project_id='42'))))


class V3(CommonIdentityTests, utils.TestCase):

    @property
    def version(self):
        return 'v3'

    @property
    def discovery_version(self):
        return '3.0'

    def get_auth_data(self, **kwargs):
        kwargs.setdefault('project_id', self.PROJECT_ID)
        token = fixture.V3Token(**kwargs)
        region = 'RegionOne'

        svc = token.add_service('identity')
        svc.add_standard_endpoints(admin=self.TEST_ADMIN_URL, region=region)

        svc = token.add_service('compute')
        svc.add_standard_endpoints(admin=self.TEST_COMPUTE_ADMIN,
                                   public=self.TEST_COMPUTE_PUBLIC,
                                   internal=self.TEST_COMPUTE_INTERNAL,
                                   region=region)

        svc = token.add_service('volumev2')
        svc.add_standard_endpoints(
            admin=self.TEST_VOLUME.versions['v2'].service.admin,
            public=self.TEST_VOLUME.versions['v2'].service.public,
            internal=self.TEST_VOLUME.versions['v2'].service.internal,
            region=region)

        svc = token.add_service('volumev3')
        svc.add_standard_endpoints(
            admin=self.TEST_VOLUME.versions['v3'].service.admin,
            public=self.TEST_VOLUME.versions['v3'].service.public,
            internal=self.TEST_VOLUME.versions['v3'].service.internal,
            region=region)

        # Add block-storage as a versioned endpoint so that we can test
        # versioned to unversioned inference.
        svc = token.add_service('block-storage')
        svc.add_standard_endpoints(
            admin=self.TEST_VOLUME.versions['v3'].service.admin,
            public=self.TEST_VOLUME.versions['v3'].service.public,
            internal=self.TEST_VOLUME.versions['v3'].service.internal,
            region=region)

        svc = token.add_service('baremetal')
        svc.add_standard_endpoints(
            internal=self.TEST_BAREMETAL_INTERNAL,
            region=region)

        return token

    def stub_auth(self, subject_token=None, **kwargs):
        if not subject_token:
            subject_token = self.TEST_TOKEN

        kwargs.setdefault('headers', {})['X-Subject-Token'] = subject_token
        self.stub_url('POST', ['auth', 'tokens'], **kwargs)

    def create_auth_plugin(self, **kwargs):
        kwargs.setdefault('auth_url', self.TEST_URL)
        kwargs.setdefault('username', self.TEST_USER)
        kwargs.setdefault('password', self.TEST_PASS)
        return identity.V3Password(**kwargs)


class V2(CommonIdentityTests, utils.TestCase):

    @property
    def version(self):
        return 'v2.0'

    @property
    def discovery_version(self):
        return '2.0'

    def create_auth_plugin(self, **kwargs):
        kwargs.setdefault('auth_url', self.TEST_URL)
        kwargs.setdefault('username', self.TEST_USER)
        kwargs.setdefault('password', self.TEST_PASS)

        try:
            kwargs.setdefault('tenant_id', kwargs.pop('project_id'))
        except KeyError:
            pass

        try:
            kwargs.setdefault('tenant_name', kwargs.pop('project_name'))
        except KeyError:
            pass

        return identity.V2Password(**kwargs)

    def get_auth_data(self, **kwargs):
        kwargs.setdefault('tenant_id', self.PROJECT_ID)
        token = fixture.V2Token(**kwargs)
        region = 'RegionOne'

        svc = token.add_service('identity')
        svc.add_endpoint(admin=self.TEST_ADMIN_URL, region=region,
                         public=None, internal=None)

        svc = token.add_service('compute')
        svc.add_endpoint(public=self.TEST_COMPUTE_PUBLIC,
                         internal=self.TEST_COMPUTE_INTERNAL,
                         admin=self.TEST_COMPUTE_ADMIN,
                         region=region)

        svc = token.add_service('volumev2')
        svc.add_endpoint(
            admin=self.TEST_VOLUME.versions['v2'].service.admin,
            public=self.TEST_VOLUME.versions['v2'].service.public,
            internal=self.TEST_VOLUME.versions['v2'].service.internal,
            region=region)

        svc = token.add_service('volumev3')
        svc.add_endpoint(
            admin=self.TEST_VOLUME.versions['v3'].service.admin,
            public=self.TEST_VOLUME.versions['v3'].service.public,
            internal=self.TEST_VOLUME.versions['v3'].service.internal,
            region=region)

        # Add block-storage as a versioned endpoint so that we can test
        # versioned to unversioned inferance.
        svc = token.add_service('block-storage')
        svc.add_endpoint(
            admin=self.TEST_VOLUME.versions['v3'].service.admin,
            public=self.TEST_VOLUME.versions['v3'].service.public,
            internal=self.TEST_VOLUME.versions['v3'].service.internal,
            region=region)

        svc = token.add_service('baremetal')
        svc.add_endpoint(
            public=None, admin=None,
            internal=self.TEST_BAREMETAL_INTERNAL,
            region=region)

        return token

    def stub_auth(self, **kwargs):
        self.stub_url('POST', ['tokens'], **kwargs)


class CatalogHackTests(utils.TestCase):

    TEST_URL = 'http://keystone.server:5000/v2.0'
    OTHER_URL = 'http://other.server:5000/path'

    IDENTITY = 'identity'

    BASE_URL = 'http://keystone.server:5000/'
    V2_URL = BASE_URL + 'v2.0'
    V3_URL = BASE_URL + 'v3'

    PROJECT_ID = uuid.uuid4().hex

    def test_getting_endpoints(self):
        disc = fixture.DiscoveryList(href=self.BASE_URL)
        self.stub_url('GET',
                      ['/'],
                      base_url=self.BASE_URL,
                      json=disc)

        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     interface='public',
                                     version=(3, 0))

        self.assertEqual(self.V3_URL, endpoint)

    def test_returns_original_when_discover_fails(self):
        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        self.stub_url('GET', [], base_url=self.BASE_URL, status_code=404)
        self.stub_url('GET', [], base_url=self.V2_URL, status_code=404)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     interface='public',
                                     version=(3, 0))

        self.assertEqual(self.V2_URL, endpoint)

    def test_getting_endpoints_project_id_and_trailing_slash_in_disc_url(self):
        # Test that when requesting a v3 endpoint and having a project in the
        # session but only the v2 endpoint with a trailing slash in the
        # catalog, we can still discover the v3 endpoint.
        disc = fixture.DiscoveryList(href=self.BASE_URL)
        self.stub_url('GET',
                      ['/'],
                      base_url=self.BASE_URL,
                      json=disc)

        # Create a project-scoped token. This will exercise the flow in the
        # discovery URL sequence where a project ID exists in the token but
        # there is no project ID in the URL.
        token = fixture.V3Token(project_id=self.PROJECT_ID)

        # Add only a v2 endpoint with a trailing slash
        service = token.add_service(self.IDENTITY)
        service.add_endpoint('public', self.V2_URL + '/')
        service.add_endpoint('admin', self.V2_URL + '/')

        # Auth with v3
        kwargs = {'headers': {'X-Subject-Token': self.TEST_TOKEN}}
        self.stub_url('POST',
                      ['auth', 'tokens'],
                      base_url=self.V3_URL,
                      json=token, **kwargs)
        v3_auth = identity.V3Password(self.V3_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)
        sess = session.Session(auth=v3_auth)

        # Try to get a v3 endpoint
        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     interface='public',
                                     version=(3, 0))
        self.assertEqual(self.V3_URL, endpoint)

    def test_returns_original_skipping_discovery(self):
        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     interface='public',
                                     skip_discovery=True,
                                     version=(3, 0))

        self.assertEqual(self.V2_URL, endpoint)

    def test_endpoint_override_skips_discovery(self):
        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        endpoint = sess.get_endpoint(endpoint_override=self.OTHER_URL,
                                     service_type=self.IDENTITY,
                                     interface='public',
                                     version=(3, 0))

        self.assertEqual(self.OTHER_URL, endpoint)

    def test_endpoint_override_data_runs_discovery(self):
        common_disc = fixture.DiscoveryList(v2=False, v3=False)
        common_disc.add_microversion(href=self.OTHER_URL, id='v2.1',
                                     min_version='2.1', max_version='2.35')

        common_m = self.stub_url('GET',
                                 base_url=self.OTHER_URL,
                                 status_code=200,
                                 json=common_disc)

        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        data = sess.get_endpoint_data(endpoint_override=self.OTHER_URL,
                                      service_type=self.IDENTITY,
                                      interface='public',
                                      min_version=(2, 0),
                                      max_version=(2, discover.LATEST))

        self.assertTrue(common_m.called)
        self.assertEqual(self.OTHER_URL, data.service_url)
        self.assertEqual(self.OTHER_URL, data.catalog_url)
        self.assertEqual(self.OTHER_URL, data.url)
        self.assertEqual((2, 1), data.min_microversion)
        self.assertEqual((2, 35), data.max_microversion)
        self.assertEqual((2, 1), data.api_version)

    def test_forcing_discovery(self):
        v2_disc = fixture.V2Discovery(self.V2_URL)
        common_disc = fixture.DiscoveryList(href=self.BASE_URL)

        v2_m = self.stub_url('GET',
                             ['v2.0'],
                             base_url=self.BASE_URL,
                             status_code=200,
                             json={'version': v2_disc})

        common_m = self.stub_url('GET',
                                 [],
                                 base_url=self.BASE_URL,
                                 status_code=300,
                                 json=common_disc)

        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        # v2 auth with v2 url doesn't make any discovery calls.
        self.assertFalse(v2_m.called)
        self.assertFalse(common_m.called)

        data = sess.get_endpoint_data(service_type=self.IDENTITY,
                                      discover_versions=True)

        # We should get the v2 document, but not the unversioned
        self.assertTrue(v2_m.called)
        self.assertFalse(common_m.called)

        # got v2 url
        self.assertEqual(self.V2_URL, data.url)
        self.assertEqual((2, 0), data.api_version)

    def test_forcing_discovery_list_returns_url(self):
        common_disc = fixture.DiscoveryList(href=self.BASE_URL)

        # 2.0 doesn't usually return a list. This is testing that if
        # the catalog url returns an endpoint that has a discovery document
        # with more than one URL and that a different url would be returned
        # by "return the latest" rules, that we get the info of the url from
        # the catalog if we don't provide a version but do provide
        # discover_versions
        v2_m = self.stub_url('GET',
                             ['v2.0'],
                             base_url=self.BASE_URL,
                             status_code=200,
                             json=common_disc)

        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        # v2 auth with v2 url doesn't make any discovery calls.
        self.assertFalse(v2_m.called)

        data = sess.get_endpoint_data(service_type=self.IDENTITY,
                                      discover_versions=True)

        # We should make the one call
        self.assertTrue(v2_m.called)

        # got v2 url
        self.assertEqual(self.V2_URL, data.url)
        self.assertEqual((2, 0), data.api_version)

    def test_latest_version_gets_latest_version(self):
        common_disc = fixture.DiscoveryList(href=self.BASE_URL)

        # 2.0 doesn't usually return a list. But we're testing version matching
        # rules, so it's nice to ensure that we don't fallback to something
        v2_m = self.stub_url('GET',
                             base_url=self.BASE_URL,
                             status_code=200,
                             json=common_disc)

        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        # v2 auth with v2 url doesn't make any discovery calls.
        self.assertFalse(v2_m.called)

        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     version='latest')

        # We should make the one call
        self.assertTrue(v2_m.called)

        # And get the v3 url
        self.assertEqual(self.V3_URL, endpoint)

        # Make sure latest logic works for min and max version
        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     max_version='latest')
        self.assertEqual(self.V3_URL, endpoint)
        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     min_version='latest')
        self.assertEqual(self.V3_URL, endpoint)
        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     min_version='latest',
                                     max_version='latest')
        self.assertEqual(self.V3_URL, endpoint)

        self.assertRaises(ValueError, sess.get_endpoint,
                          service_type=self.IDENTITY,
                          min_version='latest', max_version='3.0')

    def test_version_range(self):
        v2_disc = fixture.V2Discovery(self.V2_URL)
        common_disc = fixture.DiscoveryList(href=self.BASE_URL)

        def stub_urls():
            v2_m = self.stub_url('GET',
                                 ['v2.0'],
                                 base_url=self.BASE_URL,
                                 status_code=200,
                                 json={'version': v2_disc})
            common_m = self.stub_url('GET',
                                     base_url=self.BASE_URL,
                                     status_code=200,
                                     json=common_disc)
            return v2_m, common_m
        v2_m, common_m = stub_urls()

        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        # v2 auth with v2 url doesn't make any discovery calls.
        self.assertFalse(v2_m.called)

        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     min_version='2.0', max_version='3.0')

        # We should make the one call
        self.assertFalse(v2_m.called)
        self.assertTrue(common_m.called)

        # And get the v3 url
        self.assertEqual(self.V3_URL, endpoint)

        v2_m, common_m = stub_urls()
        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     min_version='1', max_version='2')

        # We should make no calls - we peek in the cache
        self.assertFalse(v2_m.called)
        self.assertFalse(common_m.called)

        # And get the v2 url
        self.assertEqual(self.V2_URL, endpoint)

        v2_m, common_m = stub_urls()
        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     min_version='4')

        # We should make no more calls
        self.assertFalse(v2_m.called)
        self.assertFalse(common_m.called)

        # And get no url
        self.assertIsNone(endpoint)

        v2_m, common_m = stub_urls()
        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     min_version='2')

        # We should make no more calls
        self.assertFalse(v2_m.called)
        self.assertFalse(common_m.called)

        # And get the v3 url
        self.assertEqual(self.V3_URL, endpoint)

        v2_m, common_m = stub_urls()
        self.assertRaises(ValueError, sess.get_endpoint,
                          service_type=self.IDENTITY, version=3,
                          min_version='2')

        # We should make no more calls
        self.assertFalse(v2_m.called)
        self.assertFalse(common_m.called)

    def test_get_endpoint_data(self):
        common_disc = fixture.DiscoveryList(v2=False, v3=False)
        common_disc.add_microversion(href=self.OTHER_URL, id='v2.1',
                                     min_version='2.1', max_version='2.35')

        common_m = self.stub_url('GET',
                                 base_url=self.OTHER_URL,
                                 status_code=200,
                                 json=common_disc)

        token = fixture.V2Token()
        service = token.add_service('network')
        service.add_endpoint(public=self.OTHER_URL,
                             admin=self.OTHER_URL,
                             internal=self.OTHER_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        # v2 auth with v2 url doesn't make any discovery calls.
        self.assertFalse(common_m.called)

        data = sess.get_endpoint_data(service_type='network',
                                      min_version='2.0', max_version='3.0')

        # We should make the one call
        self.assertTrue(common_m.called)

        # And get the v3 url
        self.assertEqual(self.OTHER_URL, data.url)
        self.assertEqual((2, 1), data.min_microversion)
        self.assertEqual((2, 35), data.max_microversion)
        self.assertEqual((2, 1), data.api_version)

    def test_get_endpoint_data_compute(self):
        common_disc = fixture.DiscoveryList(v2=False, v3=False)
        common_disc.add_nova_microversion(href=self.OTHER_URL, id='v2.1',
                                          min_version='2.1', version='2.35')

        common_m = self.stub_url('GET',
                                 base_url=self.OTHER_URL,
                                 status_code=200,
                                 json=common_disc)

        token = fixture.V2Token()
        service = token.add_service('compute')
        service.add_endpoint(public=self.OTHER_URL,
                             admin=self.OTHER_URL,
                             internal=self.OTHER_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        # v2 auth with v2 url doesn't make any discovery calls.
        self.assertFalse(common_m.called)

        data = sess.get_endpoint_data(service_type='compute',
                                      min_version='2.0', max_version='3.0')

        # We should make the one call
        self.assertTrue(common_m.called)

        # And get the v3 url
        self.assertEqual(self.OTHER_URL, data.url)
        self.assertEqual((2, 1), data.min_microversion)
        self.assertEqual((2, 35), data.max_microversion)
        self.assertEqual((2, 1), data.api_version)

    def test_getting_endpoints_on_auth_interface(self):
        disc = fixture.DiscoveryList(href=self.BASE_URL)
        self.stub_url('GET',
                      ['/'],
                      base_url=self.BASE_URL,
                      status_code=300,
                      json=disc)

        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        endpoint = sess.get_endpoint(interface=plugin.AUTH_INTERFACE,
                                     version=(3, 0))

        self.assertEqual(self.V3_URL, endpoint)

    def test_setting_no_discover_hack(self):
        v2_disc = fixture.V2Discovery(self.V2_URL)
        common_disc = fixture.DiscoveryList(href=self.BASE_URL)

        v2_m = self.stub_url('GET',
                             ['v2.0'],
                             base_url=self.BASE_URL,
                             status_code=200,
                             json=v2_disc)

        common_m = self.stub_url('GET',
                                 [],
                                 base_url=self.BASE_URL,
                                 status_code=300,
                                 json=common_disc)

        resp_text = uuid.uuid4().hex

        resp_m = self.stub_url('GET',
                               ['v3', 'path'],
                               base_url=self.BASE_URL,
                               status_code=200,
                               text=resp_text)

        # it doesn't matter that we auth with v2 here, discovery hack is in
        # base. All identity endpoints point to v2 urls.
        token = fixture.V2Token()
        service = token.add_service(self.IDENTITY)
        service.add_endpoint(public=self.V2_URL,
                             admin=self.V2_URL,
                             internal=self.V2_URL)

        self.stub_url('POST',
                      ['tokens'],
                      base_url=self.V2_URL,
                      json=token)

        v2_auth = identity.V2Password(self.V2_URL,
                                      username=uuid.uuid4().hex,
                                      password=uuid.uuid4().hex)

        sess = session.Session(auth=v2_auth)

        # v2 auth with v2 url doesn't make any discovery calls.
        self.assertFalse(v2_m.called)
        self.assertFalse(common_m.called)

        # v3 endpoint with hack will strip v2 suffix and call root discovery
        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     version=(3, 0),
                                     allow_version_hack=True)

        # got v3 url
        self.assertEqual(self.V3_URL, endpoint)

        # only called root discovery.
        self.assertFalse(v2_m.called)
        self.assertTrue(common_m.called_once)

        # with hack turned off it calls v2 discovery and finds nothing
        endpoint = sess.get_endpoint(service_type=self.IDENTITY,
                                     version=(3, 0),
                                     allow_version_hack=False)
        self.assertIsNone(endpoint)

        # this one called v2
        self.assertTrue(v2_m.called_once)
        self.assertTrue(common_m.called_once)

        # get_endpoint returning None raises EndpointNotFound when requesting
        self.assertRaises(exceptions.EndpointNotFound,
                          sess.get,
                          '/path',
                          endpoint_filter={'service_type': 'identity',
                                           'version': (3, 0),
                                           'allow_version_hack': False})

        self.assertFalse(resp_m.called)

        # works when allow_version_hack is set
        resp = sess.get('/path',
                        endpoint_filter={'service_type': 'identity',
                                         'version': (3, 0),
                                         'allow_version_hack': True})

        self.assertTrue(resp_m.called_once)
        self.assertEqual(resp_text, resp.text)


class GenericPlugin(plugin.BaseAuthPlugin):

    BAD_TOKEN = uuid.uuid4().hex

    def __init__(self):
        super(GenericPlugin, self).__init__()

        self.endpoint = 'http://keystone.host:5000'

        self.headers = {'headerA': 'valueA',
                        'headerB': 'valueB'}

        self.cert = '/path/to/cert'
        self.connection_params = {'cert': self.cert, 'verify': False}

    def url(self, prefix):
        return '%s/%s' % (self.endpoint, prefix)

    def get_token(self, session, **kwargs):
        # NOTE(jamielennox): by specifying get_headers this should not be used
        return self.BAD_TOKEN

    def get_headers(self, session, **kwargs):
        return self.headers

    def get_endpoint(self, session, **kwargs):
        return self.endpoint

    def get_connection_params(self, session, **kwargs):
        return self.connection_params


class GenericAuthPluginTests(utils.TestCase):

    # filter doesn't matter to GenericPlugin, but we have to specify one
    ENDPOINT_FILTER = {uuid.uuid4().hex: uuid.uuid4().hex}

    def setUp(self):
        super(GenericAuthPluginTests, self).setUp()
        self.auth = GenericPlugin()
        self.session = session.Session(auth=self.auth)

    def test_setting_headers(self):
        text = uuid.uuid4().hex
        self.stub_url('GET', base_url=self.auth.url('prefix'), text=text)

        resp = self.session.get('prefix', endpoint_filter=self.ENDPOINT_FILTER)

        self.assertEqual(text, resp.text)

        for k, v in self.auth.headers.items():
            self.assertRequestHeaderEqual(k, v)

        self.assertIsNone(self.session.get_token())
        self.assertEqual(self.auth.headers,
                         self.session.get_auth_headers())
        self.assertNotIn('X-Auth-Token',
                         self.requests_mock.last_request.headers)

    def test_setting_connection_params(self):
        text = uuid.uuid4().hex
        self.stub_url('GET', base_url=self.auth.url('prefix'), text=text)

        resp = self.session.get('prefix',
                                endpoint_filter=self.ENDPOINT_FILTER)

        self.assertEqual(text, resp.text)

        # the cert and verify values passed to request are those that were
        # returned from the auth plugin as connection params.
        self.assertEqual(self.auth.cert, self.requests_mock.last_request.cert)
        self.assertFalse(self.requests_mock.last_request.verify)

    def test_setting_bad_connection_params(self):
        # The uuid name parameter here is unknown and not in the allowed params
        # to be returned to the session and so an error will be raised.
        name = uuid.uuid4().hex
        self.auth.connection_params[name] = uuid.uuid4().hex

        e = self.assertRaises(exceptions.UnsupportedParameters,
                              self.session.get,
                              'prefix',
                              endpoint_filter=self.ENDPOINT_FILTER)

        self.assertIn(name, str(e))


class DiscoveryFailures(utils.TestCase):
    TEST_ROOT_URL = 'http://127.0.0.1:5000/'

    def test_connection_error(self):
        self.requests_mock.get(self.TEST_ROOT_URL,
                               exc=exceptions.ConnectionError)
        sess = session.Session()
        p = identity.generic.password.Password(self.TEST_ROOT_URL)
        self.assertRaises(exceptions.DiscoveryFailure, p.get_auth_ref, sess)

    def test_client_exception(self):
        self.requests_mock.get(self.TEST_ROOT_URL,
                               exc=exceptions.ClientException)
        sess = session.Session()
        p = identity.generic.password.Password(self.TEST_ROOT_URL)
        self.assertRaises(exceptions.ClientException, p.get_auth_ref, sess)

    def test_ssl_error(self):
        self.requests_mock.get(self.TEST_ROOT_URL, exc=exceptions.SSLError)
        sess = session.Session()
        p = identity.generic.password.Password(self.TEST_ROOT_URL)
        self.assertRaises(exceptions.DiscoveryFailure, p.get_auth_ref, sess)
