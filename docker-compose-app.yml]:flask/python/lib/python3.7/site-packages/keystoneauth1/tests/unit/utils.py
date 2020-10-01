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

import json as jsonutils
import logging
import time
import uuid

import fixtures
import requests
from requests_mock.contrib import fixture
from six.moves.urllib import parse as urlparse
import testtools


class TestCase(testtools.TestCase):

    TEST_DOMAIN_ID = uuid.uuid4().hex
    TEST_DOMAIN_NAME = uuid.uuid4().hex
    TEST_GROUP_ID = uuid.uuid4().hex
    TEST_ROLE_ID = uuid.uuid4().hex
    TEST_TENANT_ID = uuid.uuid4().hex
    TEST_TENANT_NAME = uuid.uuid4().hex
    TEST_RECEIPT = uuid.uuid4().hex
    TEST_TOKEN = uuid.uuid4().hex
    TEST_TRUST_ID = uuid.uuid4().hex
    TEST_USER = uuid.uuid4().hex
    TEST_USER_ID = uuid.uuid4().hex

    TEST_ROOT_URL = 'http://127.0.0.1:5000/'

    def setUp(self):
        super(TestCase, self).setUp()
        self.logger = self.useFixture(fixtures.FakeLogger(level=logging.DEBUG))

        fixtures.MockPatchObject(time, 'time', lambda: 1234)

        self.requests_mock = self.useFixture(fixture.Fixture())

    def stub_url(self, method, parts=None, base_url=None, json=None, **kwargs):
        if not base_url:
            base_url = self.TEST_URL

        if json:
            kwargs['text'] = jsonutils.dumps(json)
            headers = kwargs.setdefault('headers', {})
            headers.setdefault('Content-Type', 'application/json')

        if parts:
            url = '/'.join([p.strip('/') for p in [base_url] + parts])
        else:
            url = base_url

        url = url.replace("/?", "?")
        return self.requests_mock.register_uri(method, url, **kwargs)

    def assertRequestBodyIs(self, body=None, json=None):
        last_request_body = self.requests_mock.last_request.body
        if json:
            val = jsonutils.loads(last_request_body)
            self.assertEqual(json, val)
        elif body:
            self.assertEqual(body, last_request_body)

    def assertContentTypeIs(self, content_type):
        last_request = self.requests_mock.last_request
        self.assertEqual(last_request.headers['Content-Type'], content_type)

    def assertQueryStringIs(self, qs=''):
        r"""Verify the QueryString matches what is expected.

        The qs parameter should be of the format \'foo=bar&abc=xyz\'
        """
        expected = urlparse.parse_qs(qs, keep_blank_values=True)
        parts = urlparse.urlparse(self.requests_mock.last_request.url)
        querystring = urlparse.parse_qs(parts.query, keep_blank_values=True)
        self.assertEqual(expected, querystring)

    def assertQueryStringContains(self, **kwargs):
        """Verify the query string contains the expected parameters.

        This method is used to verify that the query string for the most recent
        request made contains all the parameters provided as ``kwargs``, and
        that the value of each parameter contains the value for the kwarg. If
        the value for the kwarg is an empty string (''), then all that's
        verified is that the parameter is present.

        """
        parts = urlparse.urlparse(self.requests_mock.last_request.url)
        qs = urlparse.parse_qs(parts.query, keep_blank_values=True)

        for k, v in kwargs.items():
            self.assertIn(k, qs)
            self.assertIn(v, qs[k])

    def assertRequestHeaderEqual(self, name, val):
        """Verify that the last request made contains a header and its value.

        The request must have already been made.
        """
        headers = self.requests_mock.last_request.headers
        self.assertEqual(headers.get(name), val)

    def assertRequestNotInHeader(self, name):
        """Verify that the last request made does not contain a header key.

        The request must have already been made.
        """
        headers = self.requests_mock.last_request.headers
        self.assertNotIn(name, headers)


class TestResponse(requests.Response):
    """Class used to wrap requests.Response.

    This provides some convenience to initialize with a dict.
    """

    def __init__(self, data):
        self._text = None
        super(TestResponse, self).__init__()
        if isinstance(data, dict):
            self.status_code = data.get('status_code', 200)
            headers = data.get('headers')
            if headers:
                self.headers.update(headers)
            # Fake the text attribute to streamline Response creation
            # _content is defined by requests.Response
            self._content = data.get('text')
        else:
            self.status_code = data

    def __eq__(self, other):
        """Define equiality behavior of request and response."""
        return self.__dict__ == other.__dict__

    # NOTE: This function is only needed by Python 2. If we get to point where
    # we don't support Python 2 anymore, this function should be removed.
    def __ne__(self, other):
        """Define inequiality behavior of request and response."""
        return not self.__eq__(other)

    @property
    def text(self):
        return self.content
