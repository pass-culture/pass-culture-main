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

import json
import re
from unittest import mock

from testtools import matchers

from keystoneauth1 import adapter
from keystoneauth1 import discover
from keystoneauth1 import exceptions
from keystoneauth1 import fixture
from keystoneauth1 import http_basic
from keystoneauth1 import noauth
from keystoneauth1 import session
from keystoneauth1.tests.unit import utils
from keystoneauth1 import token_endpoint


BASE_HOST = 'http://keystone.example.com'
BASE_URL = "%s:5000/" % BASE_HOST
UPDATED = '2013-03-06T00:00:00Z'

TEST_SERVICE_CATALOG = [{
    "endpoints": [{
        "adminURL": "%s:8774/v1.0" % BASE_HOST,
        "region": "RegionOne",
        "internalURL": "%s://127.0.0.1:8774/v1.0" % BASE_HOST,
        "publicURL": "%s:8774/v1.0/" % BASE_HOST
    }],
    "type": "nova_compat",
    "name": "nova_compat"
}, {
    "endpoints": [{
        "adminURL": "http://nova/novapi/admin",
        "region": "RegionOne",
        "internalURL": "http://nova/novapi/internal",
        "publicURL": "http://nova/novapi/public"
    }],
    "type": "compute",
    "name": "nova"
}, {
    "endpoints": [{
        "adminURL": "http://glance/glanceapi/admin",
        "region": "RegionOne",
        "internalURL": "http://glance/glanceapi/internal",
        "publicURL": "http://glance/glanceapi/public"
    }],
    "type": "image",
    "name": "glance"
}, {
    "endpoints": [{
        "adminURL": "%s:35357/v2.0" % BASE_HOST,
        "region": "RegionOne",
        "internalURL": "%s:5000/v2.0" % BASE_HOST,
        "publicURL": "%s:5000/v2.0" % BASE_HOST
    }],
    "type": "identity",
    "name": "keystone"
}, {
    "endpoints": [{
        "adminURL": "http://swift/swiftapi/admin",
        "region": "RegionOne",
        "internalURL": "http://swift/swiftapi/internal",
        "publicURL": "http://swift/swiftapi/public"
    }],
    "type": "object-store",
    "name": "swift"
}]

V2_URL = "%sv2.0" % BASE_URL
V2_VERSION = fixture.V2Discovery(V2_URL)
V2_VERSION.updated_str = UPDATED

V2_AUTH_RESPONSE = json.dumps({
    "access": {
        "token": {
            "expires": "2020-01-01T00:00:10.000123Z",
            "id": 'fakeToken',
            "tenant": {
                "id": '1'
            },
        },
        "user": {
            "id": 'test'
        },
        "serviceCatalog": TEST_SERVICE_CATALOG,
    },
})

V3_URL = "%sv3" % BASE_URL
V3_VERSION = fixture.V3Discovery(V3_URL)
V3_MEDIA_TYPES = V3_VERSION.media_types
V3_VERSION.updated_str = UPDATED

V3_AUTH_RESPONSE = json.dumps({
    "token": {
        "methods": [
            "token",
            "password"
        ],

        "expires_at": "2020-01-01T00:00:10.000123Z",
        "project": {
            "domain": {
                "id": '1',
                "name": 'test-domain'
            },
            "id": '1',
            "name": 'test-project'
        },
        "user": {
            "domain": {
                "id": '1',
                "name": 'test-domain'
            },
            "id": '1',
            "name": 'test-user'
        },
        "issued_at": "2013-05-29T16:55:21.468960Z",
    },
})

CINDER_EXAMPLES = {
    "versions": [
        {
            "status": discover.Status.CURRENT,
            "updated": "2012-01-04T11:33:21Z",
            "id": "v1.0",
            "links": [
                {
                    "href": "%sv1/" % BASE_URL,
                    "rel": "self"
                }
            ]
        },
        {
            "status": discover.Status.CURRENT,
            "updated": "2012-11-21T11:33:21Z",
            "id": "v2.0",
            "links": [
                {
                    "href": "%sv2/" % BASE_URL,
                    "rel": "self"
                }
            ]
        },
        {
            "status": discover.Status.CURRENT,
            "updated": "2012-11-21T11:33:21Z",
            "id": "v3.0",
            "version": "3.27",
            "min_version": "3.0",
            "next_min_version": "3.4",
            "not_before": "2019-12-31",
            "links": [
                {
                    "href": BASE_URL,
                    "rel": "collection"
                },
                {
                    "href": "%sv3/" % BASE_URL,
                    "rel": "self"
                }
            ]
        }
    ]
}

GLANCE_EXAMPLES = {
    "versions": [
        {
            "status": discover.Status.CURRENT,
            "id": "v2.2",
            "links": [
                {
                    "href": "%sv2/" % BASE_URL,
                    "rel": "self"
                }
            ]
        },
        {
            "status": discover.Status.SUPPORTED,
            "id": "v2.1",
            "links": [
                {
                    "href": "%sv2/" % BASE_URL,
                    "rel": "self"
                }
            ]
        },
        {
            "status": discover.Status.SUPPORTED,
            "id": "v2.0",
            "links": [
                {
                    "href": "%sv2/" % BASE_URL,
                    "rel": "self"
                }
            ]
        },
        {
            "status": discover.Status.CURRENT,
            "id": "v1.1",
            "links": [
                {
                    "href": "%sv1/" % BASE_URL,
                    "rel": "self"
                }
            ]
        },
        {
            "status": discover.Status.SUPPORTED,
            "id": "v1.0",
            "links": [
                {
                    "href": "%sv1/" % BASE_URL,
                    "rel": "self"
                }
            ]
        }
    ]
}


def _create_version_list(versions):
    return {'versions': {'values': versions}}


def _create_single_version(version):
    return {'version': version}


V3_VERSION_LIST = _create_version_list([V3_VERSION, V2_VERSION])
V2_VERSION_LIST = _create_version_list([V2_VERSION])

V3_VERSION_ENTRY = _create_single_version(V3_VERSION)
V2_VERSION_ENTRY = _create_single_version(V2_VERSION)


class CatalogHackTests(utils.TestCase):

    TEST_URL = 'http://keystone.server:5000/v2.0'
    OTHER_URL = 'http://other.server:5000/path'

    IDENTITY = 'identity'

    BASE_URL = 'http://keystone.server:5000/'
    V2_URL = BASE_URL + 'v2.0'
    V3_URL = BASE_URL + 'v3'

    def setUp(self):
        super(CatalogHackTests, self).setUp()
        self.hacks = discover._VersionHacks()
        self.hacks.add_discover_hack(self.IDENTITY,
                                     re.compile('/v2.0/?$'),
                                     '/')

    def test_version_hacks(self):
        self.assertEqual(self.BASE_URL,
                         self.hacks.get_discover_hack(self.IDENTITY,
                                                      self.V2_URL))

        self.assertEqual(self.BASE_URL,
                         self.hacks.get_discover_hack(self.IDENTITY,
                                                      self.V2_URL + '/'))

        self.assertEqual(self.OTHER_URL,
                         self.hacks.get_discover_hack(self.IDENTITY,
                                                      self.OTHER_URL))

    def test_ignored_non_service_type(self):
        self.assertEqual(self.V2_URL,
                         self.hacks.get_discover_hack('other', self.V2_URL))


class DiscoverUtils(utils.TestCase):

    def test_version_number(self):
        def assertVersion(out, inp):
            self.assertEqual(out, discover.normalize_version_number(inp))

        def versionRaises(inp):
            self.assertRaises(TypeError,
                              discover.normalize_version_number,
                              inp)

        assertVersion((1, 2), 'v1.2')
        assertVersion((11, 0), 'v11')
        assertVersion((1, 2), '1.2')
        assertVersion((1, 5, 1), '1.5.1')
        assertVersion((1, 0), '1')
        assertVersion((1, 0), 1)
        assertVersion((5, 2), 5.2)
        assertVersion((3, 20), '3.20')
        assertVersion((6, 1), (6, 1))
        assertVersion((1, 40), [1, 40])
        assertVersion((1, 0), (1,))
        assertVersion((1, 0), ['1'])
        assertVersion((discover.LATEST, discover.LATEST), 'latest')
        assertVersion((discover.LATEST, discover.LATEST), ['latest'])
        assertVersion((discover.LATEST, discover.LATEST), discover.LATEST)
        assertVersion((discover.LATEST, discover.LATEST), (discover.LATEST,))
        assertVersion((10, discover.LATEST), '10.latest')
        assertVersion((10, discover.LATEST), (10, 'latest'))
        assertVersion((10, discover.LATEST), (10, discover.LATEST))

        versionRaises(None)
        versionRaises('hello')
        versionRaises('1.a')
        versionRaises('vacuum')
        versionRaises('')
        versionRaises(('1', 'a'))

    def test_version_args(self):
        """Validate _normalize_version_args."""
        def assert_min_max(in_ver, in_min, in_max, in_type, out_min, out_max):
            self.assertEqual(
                (out_min, out_max),
                discover._normalize_version_args(
                    in_ver, in_min, in_max, service_type=in_type))

        def normalize_raises(ver, min, max, in_type):
            self.assertRaises(
                ValueError,
                discover._normalize_version_args,
                ver, min, max, service_type=in_type)

        assert_min_max(None, None, None, None,
                       None, None)
        assert_min_max(None, None, 'v1.2', None,
                       None, (1, 2))
        assert_min_max(None, 'v1.2', 'latest', None,
                       (1, 2), (discover.LATEST, discover.LATEST))
        assert_min_max(None, 'v1.2', '1.6', None,
                       (1, 2), (1, 6))
        assert_min_max(None, 'v1.2', '1.latest', None,
                       (1, 2), (1, discover.LATEST))
        assert_min_max(None, 'latest', 'latest', None,
                       (discover.LATEST, discover.LATEST),
                       (discover.LATEST, discover.LATEST))
        assert_min_max(None, 'latest', None, None,
                       (discover.LATEST, discover.LATEST),
                       (discover.LATEST, discover.LATEST))
        assert_min_max(None, (1, 2), None, None,
                       (1, 2), (discover.LATEST, discover.LATEST))
        assert_min_max('', ('1', '2'), (1, 6), None,
                       (1, 2), (1, 6))
        assert_min_max(None, ('1', '2'), (1, discover.LATEST), None,
                       (1, 2), (1, discover.LATEST))
        assert_min_max('v1.2', '', None, None,
                       (1, 2), (1, discover.LATEST))
        assert_min_max('1.latest', None, '', None,
                       (1, discover.LATEST), (1, discover.LATEST))
        assert_min_max('v1', None, None, None,
                       (1, 0), (1, discover.LATEST))
        assert_min_max('latest', None, None, None,
                       (discover.LATEST, discover.LATEST),
                       (discover.LATEST, discover.LATEST))
        assert_min_max(None, None, 'latest', 'volumev2',
                       (2, 0), (2, discover.LATEST))
        assert_min_max(None, None, None, 'volumev2',
                       (2, 0), (2, discover.LATEST))

        normalize_raises('v1', 'v2', None, None)
        normalize_raises('v1', None, 'v2', None)
        normalize_raises(None, 'latest', 'v1', None)
        normalize_raises(None, 'v1.2', 'v1.1', None)
        normalize_raises(None, 'v1.2', 1, None)
        normalize_raises('v2', None, None, 'volumev3')
        normalize_raises('v3', None, None, 'volumev2')
        normalize_raises(None, 'v2', None, 'volumev3')
        normalize_raises(None, None, 'v3', 'volumev2')

    def test_version_to_string(self):
        def assert_string(out, inp):
            self.assertEqual(out, discover.version_to_string(inp))

        assert_string('latest', (discover.LATEST,))
        assert_string('latest', (discover.LATEST, discover.LATEST))
        assert_string('latest',
                      (discover.LATEST, discover.LATEST, discover.LATEST))
        assert_string('1', (1,))
        assert_string('1.2', (1, 2))
        assert_string('1.latest', (1, discover.LATEST))

    def test_version_between(self):
        def good(minver, maxver, cand):
            self.assertTrue(discover.version_between(minver, maxver, cand))

        def bad(minver, maxver, cand):
            self.assertFalse(discover.version_between(minver, maxver, cand))

        def exc(excls, minver, maxver, cand):
            self.assertRaises(excls,
                              discover.version_between, minver, maxver, cand)

        # candidate required
        exc(ValueError, (1, 0), (1, 0), None)
        exc(ValueError, 'v1.0', '1.0', '')
        # malformed candidate
        exc(TypeError, None, None, 'bogus')
        exc(TypeError, None, None, (1, 'two'))
        # malformed min_version
        exc(TypeError, 'bogus', None, (1, 0))
        exc(TypeError, (1, 'two'), None, (1, 0))
        # malformed max_version
        exc(TypeError, None, 'bogus', (1, 0))
        exc(TypeError, None, (1, 'two'), (1, 0))

        # fail on minimum
        bad((2, 4), None, (1, 55))
        bad('v2.4', '', '2.3')
        bad('latest', None, (2, 3000))
        bad((2, discover.LATEST), '', 'v2.3000')
        bad((2, 3000), '', (1, discover.LATEST))
        bad('latest', None, 'v1000.latest')
        # fail on maximum
        bad(None, (2, 4), (2, 5))
        bad('', 'v2.4', '2.5')
        bad(None, (2, discover.LATEST), (3, 0))
        bad('', '2000.latest', 'latest')

        # candidate matches a bound
        good((1, 0), (1, 0), (1, 0))
        good('1.0', '2.9', '1.0')
        good('v1.0', 'v2.9', 'v2.9')
        # properly in between
        good((1, 0), (1, 10), (1, 2))
        good('1', '2', '1.2')
        # no lower bound
        good(None, (2, 5), (2, 3))
        # no upper bound
        good('2.5', '', '2.6')
        # no bounds at all
        good('', '', 'v1')
        good(None, None, (999, 999))
        good(None, None, 'latest')
        # Various good 'latest' scenarios
        good((discover.LATEST, discover.LATEST),
             (discover.LATEST, discover.LATEST),
             (discover.LATEST, discover.LATEST))
        good((discover.LATEST, discover.LATEST), None,
             (discover.LATEST, discover.LATEST))
        good('', 'latest', 'latest')
        good('2.latest', '3.latest', '3.0')
        good('2.latest', None, (55, 66))
        good(None, '3.latest', '3.9999')


class VersionDataTests(utils.TestCase):

    def setUp(self):
        super(VersionDataTests, self).setUp()
        self.session = session.Session()

    def test_version_data_basics(self):
        examples = {'keystone': V3_VERSION_LIST,
                    'cinder': CINDER_EXAMPLES,
                    'glance': GLANCE_EXAMPLES}

        for path, data in examples.items():
            url = "%s%s" % (BASE_URL, path)

            mock = self.requests_mock.get(url, status_code=300, json=data)

            disc = discover.Discover(self.session, url)
            raw_data = disc.raw_version_data()
            clean_data = disc.version_data()

            for v in raw_data:
                for n in ('id', 'status', 'links'):
                    msg = '%s missing from %s version data' % (n, path)
                    self.assertThat(v, matchers.Annotate(msg,
                                                         matchers.Contains(n)))

            for v in clean_data:
                for n in ('version', 'url', 'raw_status'):
                    msg = '%s missing from %s version data' % (n, path)
                    self.assertThat(v, matchers.Annotate(msg,
                                                         matchers.Contains(n)))

            self.assertTrue(mock.called_once)

    def test_version_data_override_version_url(self):
        # if the request url is versioned already, just return it.
        self.requests_mock.get(
            V3_URL, status_code=200,
            json={'version': fixture.V3Discovery('http://override/identity/v3')
                  }
        )

        disc = discover.Discover(self.session, V3_URL)
        version_data = disc.version_data()

        for v in version_data:
            self.assertEqual(v['version'], (3, 0))
            self.assertEqual(v['status'], discover.Status.CURRENT)
            self.assertEqual(v['raw_status'], 'stable')
            self.assertEqual(v['url'], V3_URL)

        # if the request url is not versioned, just add version info to it.(
        # do not changed the url's netloc or path)
        self.requests_mock.get(
            BASE_URL, status_code=200,
            json={'version': fixture.V3Discovery('http://override/identity/v3')
                  }
        )

        disc = discover.Discover(self.session, BASE_URL)
        version_data = disc.version_data()

        for v in version_data:
            self.assertEqual(v['version'], (3, 0))
            self.assertEqual(v['status'], discover.Status.CURRENT)
            self.assertEqual(v['raw_status'], 'stable')
            self.assertEqual(v['url'], V3_URL)

    def test_version_data_unknown(self):
        discovery_fixture = fixture.V3Discovery(V3_URL)
        discovery_fixture.status = 'hungry'
        discovery_doc = _create_single_version(discovery_fixture)

        self.requests_mock.get(V3_URL, status_code=200, json=discovery_doc)

        disc = discover.Discover(self.session, V3_URL)
        clean_data = disc.version_data(allow_unknown=True)

        self.assertEqual(discover.Status.UNKNOWN, clean_data[0]['status'])

    def test_version_data_individual(self):
        mock = self.requests_mock.get(V3_URL,
                                      status_code=200,
                                      json=V3_VERSION_ENTRY)

        disc = discover.Discover(self.session, V3_URL)
        raw_data = disc.raw_version_data()
        clean_data = disc.version_data()

        for v in raw_data:
            self.assertEqual(v['id'], 'v3.0')
            self.assertEqual(v['status'], 'stable')
            self.assertIn('media-types', v)
            self.assertIn('links', v)

        for v in clean_data:
            self.assertEqual(v['version'], (3, 0))
            self.assertEqual(v['status'], discover.Status.CURRENT)
            self.assertEqual(v['raw_status'], 'stable')
            self.assertEqual(v['url'], V3_URL)

        self.assertTrue(mock.called_once)

    def test_version_data_legacy_ironic_no_override(self):
        """Validate detection of legacy Ironic microversion ranges."""
        ironic_url = 'https://bare-metal.example.com/v1/'
        self.requests_mock.get(
            ironic_url, status_code=200,
            json={
                'id': 'v1',
                'links': [{
                    "href": ironic_url,
                    "rel": "self"}]},
            headers={
                'X-OpenStack-Ironic-API-Minimum-Version': '1.3',
                'X-OpenStack-Ironic-API-Maximum-Version': '1.21',
            })

        plugin = noauth.NoAuth()
        a = adapter.Adapter(
            self.session,
            auth=plugin,
            service_type='baremetal')

        self.assertIsNone(a.get_api_major_version())

    def test_version_data_ironic_microversions(self):
        """Validate detection of Ironic microversion ranges."""
        ironic_url = 'https://bare-metal.example.com/v1/'
        self.requests_mock.get(
            ironic_url, status_code=200,
            json={
                'id': 'v1',
                'version': {
                    'id': 'v1',
                    'links': [{
                        "href": ironic_url,
                        "rel": "self"}],
                    'version': '1.40',
                    'min_version': '1.10',
                    'status': 'CURRENT',
                },
                'links': [{
                    "href": ironic_url,
                    "rel": "self"}],
            },
            # Keep headers so we can verify that body trumps headers
            headers={
                'X-OpenStack-Ironic-API-Minimum-Version': '1.3',
                'X-OpenStack-Ironic-API-Maximum-Version': '1.21',
            })

        self.assertEqual(
            [
                {
                    'collection': None,
                    'version': (1, 0),
                    'url': ironic_url,
                    'status': discover.Status.CURRENT,
                    'raw_status': discover.Status.CURRENT,
                    'min_microversion': (1, 10),
                    'max_microversion': (1, 40),
                    'next_min_version': None,
                    'not_before': None,
                },
            ],
            discover.Discover(self.session, ironic_url).version_data())

    def test_version_data_legacy_ironic_microversions(self):
        """Validate detection of legacy Ironic microversion ranges."""
        ironic_url = 'https://bare-metal.example.com/v1/'
        self.requests_mock.get(
            ironic_url, status_code=200,
            json={
                'id': 'v1',
                'links': [{
                    "href": ironic_url,
                    "rel": "self"}]},
            headers={
                'X-OpenStack-Ironic-API-Minimum-Version': '1.3',
                'X-OpenStack-Ironic-API-Maximum-Version': '1.21',
            })

        self.assertEqual(
            [
                {
                    'collection': None,
                    'version': (1, 0),
                    'url': ironic_url,
                    'status': discover.Status.CURRENT,
                    'raw_status': discover.Status.CURRENT,
                    'min_microversion': (1, 3),
                    'max_microversion': (1, 21),
                    'next_min_version': None,
                    'not_before': None,
                },
            ],
            discover.Discover(self.session, ironic_url).version_data())

    def test_version_data_microversions(self):
        """Validate [min_|max_]version conversion to {min|max}_microversion."""
        def setup_mock(versions_in):
            # Set up the test data with the input version data
            jsondata = {
                "versions": [
                    dict(
                        {
                            "status": discover.Status.CURRENT,
                            "id": "v2.2",
                            "links": [
                                {
                                    "href": V3_URL,
                                    "rel": "self"
                                }
                            ]
                        },
                        **versions_in
                    )
                ]
            }
            self.requests_mock.get(
                V3_URL, status_code=200, json=jsondata)

        def test_ok(versions_in, versions_out):
            setup_mock(versions_in)
            # Ensure the output contains the expected microversions
            self.assertEqual(
                [
                    dict(
                        {
                            'collection': None,
                            'version': (2, 2),
                            'url': V3_URL,
                            'status': discover.Status.CURRENT,
                            'raw_status': discover.Status.CURRENT,
                        },
                        **versions_out
                    )
                ],
                discover.Discover(self.session, V3_URL).version_data())

        def test_exc(versions_in):
            setup_mock(versions_in)
            # Ensure TypeError is raised
            self.assertRaises(
                TypeError,
                discover.Discover(self.session, V3_URL).version_data)

        # no version info in input
        test_ok({},
                {'min_microversion': None, 'max_microversion': None,
                 'next_min_version': None, 'not_before': None})

        # version => max_microversion
        test_ok({'version': '2.2'},
                {'min_microversion': None, 'max_microversion': (2, 2),
                 'next_min_version': None, 'not_before': None})

        # max_version supersedes version (even if malformed).  min_version &
        # normalization.
        test_ok({'min_version': '2', 'version': 'foo', 'max_version': '2.2'},
                {'min_microversion': (2, 0), 'max_microversion': (2, 2),
                 'next_min_version': None, 'not_before': None})

        # Edge case: min/max_version ignored if present but "empty"; version
        # used for max_microversion.
        test_ok({'min_version': '', 'version': '2.1', 'max_version': ''},
                {'min_microversion': None, 'max_microversion': (2, 1),
                 'next_min_version': None, 'not_before': None})

        # next_min_version set
        test_ok({'min_version': '2', 'max_version': '2.2',
                 'next_min_version': '2.1', 'not_before': '2019-07-01'},
                {'min_microversion': (2, 0), 'max_microversion': (2, 2),
                 'next_min_version': (2, 1), 'not_before': '2019-07-01'})

        # Badly-formatted min_version
        test_exc({'min_version': 'foo', 'max_version': '2.1'})

        # Badly-formatted max_version
        test_exc({'min_version': '2.1', 'max_version': 'foo'})

        # Badly-formatted version (when max_version omitted)
        test_exc({'min_version': '2.1', 'version': 'foo'})

        # Badly-formatted next_min_version
        test_exc({'next_min_version': 'bogus', 'not_before': '2019-07-01'})

    def test_endpoint_data_noauth_discover(self):
        mock = self.requests_mock.get(
            BASE_URL, status_code=200, json=V3_VERSION_LIST)
        self.requests_mock.get(
            V3_URL, status_code=200, json=V3_VERSION_ENTRY)

        plugin = noauth.NoAuth(endpoint=BASE_URL)
        data = plugin.get_endpoint_data(self.session)

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(plugin.get_api_major_version(self.session), (3, 0))
        self.assertEqual(plugin.get_endpoint(self.session), BASE_URL)

        self.assertTrue(mock.called_once)

    def test_endpoint_data_noauth_versioned_discover(self):
        self.requests_mock.get(
            BASE_URL, status_code=200, json=V3_VERSION_LIST)
        self.requests_mock.get(
            V3_URL, status_code=200, json=V3_VERSION_ENTRY)

        plugin = noauth.NoAuth(endpoint=V3_URL)
        data = plugin.get_endpoint_data(self.session)

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(plugin.get_api_major_version(self.session), (3, 0))
        self.assertEqual(plugin.get_endpoint(self.session), V3_URL)

    def test_endpoint_data_noauth_no_discover(self):
        plugin = noauth.NoAuth(endpoint=V3_URL)
        data = plugin.get_endpoint_data(
            self.session, discover_versions=False)

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(plugin.get_api_major_version(self.session), (3, 0))
        self.assertEqual(plugin.get_endpoint(self.session), V3_URL)

    def test_endpoint_data_noauth_override_no_discover(self):
        plugin = noauth.NoAuth()
        data = plugin.get_endpoint_data(
            self.session, endpoint_override=V3_URL, discover_versions=False)

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(
            plugin.get_endpoint(self.session, endpoint_override=V3_URL),
            V3_URL)

    def test_endpoint_data_http_basic_discover(self):
        self.requests_mock.get(
            BASE_URL, status_code=200, json=V3_VERSION_LIST)
        self.requests_mock.get(
            V3_URL, status_code=200, json=V3_VERSION_ENTRY)

        plugin = http_basic.HTTPBasicAuth(endpoint=V3_URL)
        data = plugin.get_endpoint_data(self.session)

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(plugin.get_api_major_version(self.session), (3, 0))
        self.assertEqual(plugin.get_endpoint(self.session), V3_URL)

    def test_endpoint_data_http_basic_no_discover(self):
        plugin = http_basic.HTTPBasicAuth(endpoint=V3_URL)
        data = plugin.get_endpoint_data(
            self.session, discover_versions=False)

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(plugin.get_api_major_version(self.session), (3, 0))
        self.assertEqual(plugin.get_endpoint(self.session), V3_URL)

    def test_endpoint_data_http_basic_override_no_discover(self):
        plugin = http_basic.HTTPBasicAuth()
        data = plugin.get_endpoint_data(
            self.session, endpoint_override=V3_URL, discover_versions=False)

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(
            plugin.get_api_major_version(
                self.session, endpoint_override=V3_URL),
            (3, 0))
        self.assertEqual(
            plugin.get_endpoint(self.session, endpoint_override=V3_URL),
            V3_URL)

    def test_endpoint_data_noauth_adapter(self):
        self.requests_mock.get(
            BASE_URL, status_code=200, json=V3_VERSION_LIST)
        self.requests_mock.get(
            V3_URL, status_code=200, json=V3_VERSION_ENTRY)

        client = adapter.Adapter(
            session.Session(noauth.NoAuth()),
            endpoint_override=BASE_URL)
        data = client.get_endpoint_data()

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(client.get_api_major_version(), (3, 0))
        self.assertEqual(client.get_endpoint(), BASE_URL)

    def test_endpoint_data_noauth_versioned_adapter(self):
        mock = self.requests_mock.get(
            V3_URL, status_code=200, json=V3_VERSION_ENTRY)

        client = adapter.Adapter(
            session.Session(noauth.NoAuth()),
            endpoint_override=V3_URL)
        data = client.get_endpoint_data()

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(client.get_api_major_version(), (3, 0))
        self.assertEqual(client.get_endpoint(), V3_URL)

        self.assertTrue(mock.called_once)

    def test_endpoint_data_token_endpoint_discover(self):
        mock = self.requests_mock.get(
            V3_URL, status_code=200, json=V3_VERSION_ENTRY)
        plugin = token_endpoint.Token(endpoint=V3_URL, token='bogus')
        data = plugin.get_endpoint_data(self.session)

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(plugin.get_api_major_version(self.session), (3, 0))
        self.assertEqual(plugin.get_endpoint(self.session), V3_URL)

        self.assertTrue(mock.called_once)

    def test_endpoint_data_token_endpoint_no_discover(self):
        plugin = token_endpoint.Token(endpoint=V3_URL, token='bogus')
        data = plugin.get_endpoint_data(self.session, discover_versions=False)

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(plugin.get_api_major_version(self.session), (3, 0))
        self.assertEqual(plugin.get_endpoint(self.session), V3_URL)

    def test_endpoint_data_token_endpoint_adapter(self):
        mock = self.requests_mock.get(
            V3_URL, status_code=200, json=V3_VERSION_ENTRY)
        plugin = token_endpoint.Token(endpoint=V3_URL, token='bogus')

        client = adapter.Adapter(session.Session(plugin))
        data = client.get_endpoint_data()

        self.assertEqual(data.api_version, (3, 0))
        self.assertEqual(data.url, V3_URL)
        self.assertEqual(client.get_api_major_version(), (3, 0))
        self.assertEqual(client.get_endpoint(), V3_URL)

        self.assertTrue(mock.called_once)

    def test_data_for_url(self):
        mock = self.requests_mock.get(V3_URL,
                                      status_code=200,
                                      json=V3_VERSION_ENTRY)

        disc = discover.Discover(self.session, V3_URL)
        for url in (V3_URL, V3_URL + '/'):
            data = disc.versioned_data_for(url=url)
            self.assertEqual(data['version'], (3, 0))
            self.assertEqual(data['raw_status'], 'stable')
            self.assertEqual(data['url'], V3_URL)

        self.assertTrue(mock.called_once)

    def test_data_for_no_version(self):
        mock = self.requests_mock.get(V3_URL,
                                      status_code=200,
                                      json=V3_VERSION_ENTRY)

        disc = discover.Discover(self.session, V3_URL)

        data = disc.versioned_data_for()
        self.assertEqual(data['version'], (3, 0))
        self.assertEqual(data['raw_status'], 'stable')
        self.assertEqual(data['url'], V3_URL)
        self.assertRaises(TypeError, disc.data_for, version=None)

        self.assertTrue(mock.called_once)

    def test_keystone_version_data(self):
        mock = self.requests_mock.get(BASE_URL,
                                      status_code=300,
                                      json=V3_VERSION_LIST)

        disc = discover.Discover(self.session, BASE_URL)
        raw_data = disc.raw_version_data()
        clean_data = disc.version_data()

        self.assertEqual(2, len(raw_data))
        self.assertEqual(2, len(clean_data))

        for v in raw_data:
            self.assertIn(v['id'], ('v2.0', 'v3.0'))
            self.assertEqual(v['updated'], UPDATED)
            self.assertEqual(v['status'], 'stable')

            if v['id'] == 'v3.0':
                self.assertEqual(v['media-types'], V3_MEDIA_TYPES)

        for v in clean_data:
            self.assertIn(v['version'], ((2, 0), (3, 0)))
            self.assertEqual(v['raw_status'], 'stable')

        valid_v3_versions = (
            disc.data_for('v3.0'),
            disc.data_for('3.latest'),
            disc.data_for('latest'),
            disc.versioned_data_for(min_version='v3.0',
                                    max_version='v3.latest'),
            disc.versioned_data_for(min_version='3'),
            disc.versioned_data_for(min_version='3.latest'),
            disc.versioned_data_for(min_version='latest'),
            disc.versioned_data_for(min_version='3.latest',
                                    max_version='latest'),
            disc.versioned_data_for(min_version='latest',
                                    max_version='latest'),
            disc.versioned_data_for(min_version=2),
            disc.versioned_data_for(min_version='2.latest'))
        for version in valid_v3_versions:
            self.assertEqual((3, 0), version['version'])
            self.assertEqual('stable', version['raw_status'])
            self.assertEqual(V3_URL, version['url'])

        valid_v2_versions = (
            disc.data_for(2),
            disc.data_for('2.latest'),
            disc.versioned_data_for(min_version=2,
                                    max_version=(2, discover.LATEST)),
            disc.versioned_data_for(min_version='2.latest',
                                    max_version='2.latest'))
        for version in valid_v2_versions:
            self.assertEqual((2, 0), version['version'])
            self.assertEqual('stable', version['raw_status'])
            self.assertEqual(V2_URL, version['url'])

        self.assertIsNone(disc.url_for('v4'))
        self.assertIsNone(disc.versioned_url_for(
            min_version='v4', max_version='v4.latest'))
        self.assertEqual(V3_URL, disc.url_for('v3'))
        self.assertEqual(V3_URL, disc.versioned_url_for(
            min_version='v3', max_version='v3.latest'))
        self.assertEqual(V2_URL, disc.url_for('v2'))
        self.assertEqual(V2_URL, disc.versioned_url_for(
            min_version='v2', max_version='v2.latest'))

        self.assertTrue(mock.called_once)

    def test_cinder_version_data(self):
        mock = self.requests_mock.get(BASE_URL,
                                      status_code=300,
                                      json=CINDER_EXAMPLES)

        disc = discover.Discover(self.session, BASE_URL)
        raw_data = disc.raw_version_data()
        clean_data = disc.version_data()

        self.assertEqual(3, len(raw_data))

        for v in raw_data:
            self.assertEqual(v['status'], discover.Status.CURRENT)
            if v['id'] == 'v1.0':
                self.assertEqual(v['updated'], '2012-01-04T11:33:21Z')
            elif v['id'] == 'v2.0':
                self.assertEqual(v['updated'], '2012-11-21T11:33:21Z')
            elif v['id'] == 'v3.0':
                self.assertEqual(v['updated'], '2012-11-21T11:33:21Z')
            else:
                self.fail("Invalid version found")

        v1_url = "%sv1/" % BASE_URL
        v2_url = "%sv2/" % BASE_URL
        v3_url = "%sv3/" % BASE_URL

        self.assertEqual(clean_data, [
            {
                'collection': None,
                'max_microversion': None,
                'min_microversion': None,
                'next_min_version': None,
                'not_before': None,
                'version': (1, 0),
                'url': v1_url,
                'status': discover.Status.CURRENT,
                'raw_status': discover.Status.CURRENT,
            },
            {
                'collection': None,
                'max_microversion': None,
                'min_microversion': None,
                'next_min_version': None,
                'not_before': None,
                'version': (2, 0),
                'url': v2_url,
                'status': discover.Status.CURRENT,
                'raw_status': discover.Status.CURRENT,
            },
            {
                'collection': BASE_URL,
                'max_microversion': (3, 27),
                'min_microversion': (3, 0),
                'next_min_version': (3, 4),
                'not_before': u'2019-12-31',
                'version': (3, 0),
                'url': v3_url,
                'status': discover.Status.CURRENT,
                'raw_status': discover.Status.CURRENT,
            },
        ])

        for version in (disc.data_for('v2.0'),
                        disc.versioned_data_for(min_version='v2.0',
                                                max_version='v2.latest')):
            self.assertEqual((2, 0), version['version'])
            self.assertEqual(discover.Status.CURRENT, version['raw_status'])
            self.assertEqual(v2_url, version['url'])

        for version in (disc.data_for(1),
                        disc.versioned_data_for(
                            min_version=(1,),
                            max_version=(1, discover.LATEST))):
            self.assertEqual((1, 0), version['version'])
            self.assertEqual(discover.Status.CURRENT, version['raw_status'])
            self.assertEqual(v1_url, version['url'])

        self.assertIsNone(disc.url_for('v4'))
        self.assertIsNone(disc.versioned_url_for(min_version='v4',
                                                 max_version='v4.latest'))
        self.assertEqual(v3_url, disc.url_for('v3'))
        self.assertEqual(v3_url, disc.versioned_url_for(
            min_version='v3', max_version='v3.latest'))
        self.assertEqual(v2_url, disc.url_for('v2'))
        self.assertEqual(v2_url, disc.versioned_url_for(
            min_version='v2', max_version='v2.latest'))
        self.assertEqual(v1_url, disc.url_for('v1'))
        self.assertEqual(v1_url, disc.versioned_url_for(
            min_version='v1', max_version='v1.latest'))

        self.assertTrue(mock.called_once)

    def test_glance_version_data(self):
        mock = self.requests_mock.get(BASE_URL,
                                      status_code=200,
                                      json=GLANCE_EXAMPLES)

        disc = discover.Discover(self.session, BASE_URL)
        raw_data = disc.raw_version_data()
        clean_data = disc.version_data()

        self.assertEqual(5, len(raw_data))

        for v in raw_data:
            if v['id'] in ('v2.2', 'v1.1'):
                self.assertEqual(v['status'], discover.Status.CURRENT)
            elif v['id'] in ('v2.1', 'v2.0', 'v1.0'):
                self.assertEqual(v['status'], discover.Status.SUPPORTED)
            else:
                self.fail("Invalid version found")

        v1_url = '%sv1/' % BASE_URL
        v2_url = '%sv2/' % BASE_URL

        self.assertEqual(clean_data, [
            {
                'collection': None,
                'max_microversion': None,
                'min_microversion': None,
                'next_min_version': None,
                'not_before': None,
                'version': (1, 0),
                'url': v1_url,
                'status': discover.Status.SUPPORTED,
                'raw_status': discover.Status.SUPPORTED,
            },
            {
                'collection': None,
                'max_microversion': None,
                'min_microversion': None,
                'next_min_version': None,
                'not_before': None,
                'version': (1, 1),
                'url': v1_url,
                'status': discover.Status.CURRENT,
                'raw_status': discover.Status.CURRENT,
            },
            {
                'collection': None,
                'max_microversion': None,
                'min_microversion': None,
                'next_min_version': None,
                'not_before': None,
                'version': (2, 0),
                'url': v2_url,
                'status': discover.Status.SUPPORTED,
                'raw_status': discover.Status.SUPPORTED,
            },
            {
                'collection': None,
                'max_microversion': None,
                'min_microversion': None,
                'next_min_version': None,
                'not_before': None,
                'version': (2, 1),
                'url': v2_url,
                'status': discover.Status.SUPPORTED,
                'raw_status': discover.Status.SUPPORTED,
            },
            {
                'collection': None,
                'max_microversion': None,
                'min_microversion': None,
                'next_min_version': None,
                'not_before': None,
                'version': (2, 2),
                'url': v2_url,
                'status': discover.Status.CURRENT,
                'raw_status': discover.Status.CURRENT,
            },
        ])

        for ver in (2, 2.1, 2.2):
            for version in (disc.data_for(ver),
                            disc.versioned_data_for(
                                min_version=ver,
                                max_version=(2, discover.LATEST))):
                self.assertEqual((2, 2), version['version'])
                self.assertEqual(
                    discover.Status.CURRENT, version['raw_status']
                )
                self.assertEqual(v2_url, version['url'])
                self.assertEqual(v2_url, disc.url_for(ver))

        for ver in (1, 1.1):
            for version in (disc.data_for(ver),
                            disc.versioned_data_for(
                                min_version=ver,
                                max_version=(1, discover.LATEST))):
                self.assertEqual((1, 1), version['version'])
                self.assertEqual(
                    discover.Status.CURRENT, version['raw_status']
                )
                self.assertEqual(v1_url, version['url'])
                self.assertEqual(v1_url, disc.url_for(ver))

        self.assertIsNone(disc.url_for('v3'))
        self.assertIsNone(disc.versioned_url_for(min_version='v3',
                                                 max_version='v3.latest'))
        self.assertIsNone(disc.url_for('v2.3'))
        self.assertIsNone(disc.versioned_url_for(min_version='v2.3',
                                                 max_version='v2.latest'))

        self.assertTrue(mock.called_once)

    def test_allow_deprecated(self):
        status = 'deprecated'
        version_list = [{'id': 'v3.0',
                         'links': [{'href': V3_URL, 'rel': 'self'}],
                         'media-types': V3_MEDIA_TYPES,
                         'status': status,
                         'updated': UPDATED}]
        self.requests_mock.get(BASE_URL, json={'versions': version_list})

        disc = discover.Discover(self.session, BASE_URL)

        # deprecated is allowed by default
        versions = disc.version_data(allow_deprecated=False)
        self.assertEqual(0, len(versions))

        versions = disc.version_data(allow_deprecated=True)
        self.assertEqual(1, len(versions))
        self.assertEqual(status, versions[0]['raw_status'])
        self.assertEqual(V3_URL, versions[0]['url'])
        self.assertEqual((3, 0), versions[0]['version'])

    def test_allow_experimental(self):
        status = 'experimental'
        version_list = [{'id': 'v3.0',
                         'links': [{'href': V3_URL, 'rel': 'self'}],
                         'media-types': V3_MEDIA_TYPES,
                         'status': status,
                         'updated': UPDATED}]
        self.requests_mock.get(BASE_URL, json={'versions': version_list})

        disc = discover.Discover(self.session, BASE_URL)

        versions = disc.version_data()
        self.assertEqual(0, len(versions))

        versions = disc.version_data(allow_experimental=True)
        self.assertEqual(1, len(versions))
        self.assertEqual(status, versions[0]['raw_status'])
        self.assertEqual(V3_URL, versions[0]['url'])
        self.assertEqual((3, 0), versions[0]['version'])

    def test_allow_unknown(self):
        status = 'abcdef'
        version_list = fixture.DiscoveryList(BASE_URL,
                                             v2=False,
                                             v3_status=status)
        self.requests_mock.get(BASE_URL, json=version_list)

        disc = discover.Discover(self.session, BASE_URL)

        versions = disc.version_data()
        self.assertEqual(0, len(versions))

        versions = disc.version_data(allow_unknown=True)
        self.assertEqual(1, len(versions))
        self.assertEqual(status, versions[0]['raw_status'])
        self.assertEqual(V3_URL, versions[0]['url'])
        self.assertEqual((3, 0), versions[0]['version'])

    def test_ignoring_invalid_links(self):
        version_list = [{'id': 'v3.0',
                         'links': [{'href': V3_URL, 'rel': 'self'}],
                         'media-types': V3_MEDIA_TYPES,
                         'status': 'stable',
                         'updated': UPDATED},
                        {'id': 'v3.1',
                         'media-types': V3_MEDIA_TYPES,
                         'status': 'stable',
                         'updated': UPDATED},
                        {'media-types': V3_MEDIA_TYPES,
                         'status': 'stable',
                         'updated': UPDATED,
                         'links': [{'href': V3_URL, 'rel': 'self'}],
                         }]

        self.requests_mock.get(BASE_URL, json={'versions': version_list})

        disc = discover.Discover(self.session, BASE_URL)

        # raw_version_data will return all choices, even invalid ones
        versions = disc.raw_version_data()
        self.assertEqual(3, len(versions))

        # only the version with both id and links will be actually returned
        versions = disc.version_data()
        self.assertEqual(1, len(versions))


class EndpointDataTests(utils.TestCase):
    @mock.patch('keystoneauth1.discover.get_discovery')
    @mock.patch('keystoneauth1.discover.EndpointData.'
                '_get_discovery_url_choices')
    def test_run_discovery_cache(self, mock_url_choices, mock_get_disc):
        # get_discovery raises so we keep looping
        mock_get_disc.side_effect = exceptions.DiscoveryFailure()
        # Duplicate 'url1' in here to validate the cache behavior
        mock_url_choices.return_value = ('url1', 'url2', 'url1', 'url3')
        epd = discover.EndpointData()
        epd._run_discovery(
            session='sess', cache='cache', min_version='min',
            max_version='max', project_id='projid',
            allow_version_hack='allow_hack', discover_versions='disc_vers')
        # Only one call with 'url1'
        self.assertEqual(3, mock_get_disc.call_count)
        mock_get_disc.assert_has_calls(
            [mock.call('sess', url, cache='cache', authenticated=False)
             for url in ('url1', 'url2', 'url3')])

    def test_run_discovery_auth(self):
        url = 'https://example.com'
        headers = {'Accept': 'application/json'}

        session = mock.Mock()
        session.get.side_effect = [
            exceptions.Unauthorized('unauthorized'),
            # Throw a different exception the second time so that we can
            # catch it in the test and verify the retry.
            exceptions.BadRequest('bad request'),
        ]

        try:
            discover.get_version_data(session, url)
        except exceptions.BadRequest:
            pass
        # Only one call with 'url'
        self.assertEqual(2, session.get.call_count)
        session.get.assert_has_calls([
            mock.call(url, headers=headers, authenticated=None),
            mock.call(url, headers=headers, authenticated=True),
        ])

    def test_endpoint_data_str(self):
        """Validate EndpointData.__str__."""
        # Populate a few fields to make sure they come through.
        epd = discover.EndpointData(catalog_url='abc', service_type='123',
                                    api_version=(2, 3))
        exp = (
            'EndpointData{api_version=(2, 3), catalog_url=abc,'
            ' endpoint_id=None, interface=None, major_version=None,'
            ' max_microversion=None, min_microversion=None,'
            ' next_min_version=None, not_before=None, raw_endpoint=None,'
            ' region_name=None, service_id=None, service_name=None,'
            ' service_type=123, service_url=None, url=abc}')
        # Works with str()
        self.assertEqual(exp, str(epd))
        # Works with implicit stringification
        self.assertEqual(exp, "%s" % epd)

    def test_project_id_int_fallback(self):
        bad_url = "https://compute.example.com/v2/123456"
        epd = discover.EndpointData(catalog_url=bad_url)
        self.assertEqual((2, 0), epd.api_version)
