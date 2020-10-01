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

import datetime
import itertools
import json
import logging
import sys
from unittest import mock
import uuid

from oslo_utils import encodeutils
import requests
import requests.auth
import six
from testtools import matchers

from keystoneauth1 import adapter
from keystoneauth1 import discover
from keystoneauth1 import exceptions
from keystoneauth1 import plugin
from keystoneauth1 import session as client_session
from keystoneauth1.tests.unit import utils
from keystoneauth1 import token_endpoint


class RequestsAuth(requests.auth.AuthBase):

    def __init__(self, *args, **kwargs):
        super(RequestsAuth, self).__init__(*args, **kwargs)
        self.header_name = uuid.uuid4().hex
        self.header_val = uuid.uuid4().hex
        self.called = False

    def __call__(self, request):
        request.headers[self.header_name] = self.header_val
        self.called = True
        return request


class SessionTests(utils.TestCase):

    TEST_URL = 'http://127.0.0.1:5000/'

    def test_get(self):
        session = client_session.Session()
        self.stub_url('GET', text='response')
        resp = session.get(self.TEST_URL)

        self.assertEqual('GET', self.requests_mock.last_request.method)
        self.assertEqual(resp.text, 'response')
        self.assertTrue(resp.ok)

    def test_post(self):
        session = client_session.Session()
        self.stub_url('POST', text='response')
        resp = session.post(self.TEST_URL, json={'hello': 'world'})

        self.assertEqual('POST', self.requests_mock.last_request.method)
        self.assertEqual(resp.text, 'response')
        self.assertTrue(resp.ok)
        self.assertRequestBodyIs(json={'hello': 'world'})

    def test_head(self):
        session = client_session.Session()
        self.stub_url('HEAD')
        resp = session.head(self.TEST_URL)

        self.assertEqual('HEAD', self.requests_mock.last_request.method)
        self.assertTrue(resp.ok)
        self.assertRequestBodyIs('')

    def test_put(self):
        session = client_session.Session()
        self.stub_url('PUT', text='response')
        resp = session.put(self.TEST_URL, json={'hello': 'world'})

        self.assertEqual('PUT', self.requests_mock.last_request.method)
        self.assertEqual(resp.text, 'response')
        self.assertTrue(resp.ok)
        self.assertRequestBodyIs(json={'hello': 'world'})

    def test_delete(self):
        session = client_session.Session()
        self.stub_url('DELETE', text='response')
        resp = session.delete(self.TEST_URL)

        self.assertEqual('DELETE', self.requests_mock.last_request.method)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.text, 'response')

    def test_patch(self):
        session = client_session.Session()
        self.stub_url('PATCH', text='response')
        resp = session.patch(self.TEST_URL, json={'hello': 'world'})

        self.assertEqual('PATCH', self.requests_mock.last_request.method)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.text, 'response')
        self.assertRequestBodyIs(json={'hello': 'world'})

    def test_set_microversion_headers(self):

        # String microversion, specified service type
        headers = {}
        client_session.Session._set_microversion_headers(
            headers, '2.30', 'compute', None)
        self.assertEqual(headers['OpenStack-API-Version'], 'compute 2.30')
        self.assertEqual(headers['X-OpenStack-Nova-API-Version'], '2.30')
        self.assertEqual(len(headers.keys()), 2)

        # Tuple microversion, service type via endpoint_filter
        headers = {}
        client_session.Session._set_microversion_headers(
            headers, (2, 30), None, {'service_type': 'compute'})
        self.assertEqual(headers['OpenStack-API-Version'], 'compute 2.30')
        self.assertEqual(headers['X-OpenStack-Nova-API-Version'], '2.30')
        self.assertEqual(len(headers.keys()), 2)

        # 'latest' (string) microversion
        headers = {}
        client_session.Session._set_microversion_headers(
            headers, 'latest', 'compute', None)
        self.assertEqual(headers['OpenStack-API-Version'], 'compute latest')
        self.assertEqual(headers['X-OpenStack-Nova-API-Version'], 'latest')
        self.assertEqual(len(headers.keys()), 2)

        # LATEST (tuple) microversion
        headers = {}
        client_session.Session._set_microversion_headers(
            headers, (discover.LATEST, discover.LATEST), 'compute', None)
        self.assertEqual(headers['OpenStack-API-Version'], 'compute latest')
        self.assertEqual(headers['X-OpenStack-Nova-API-Version'], 'latest')
        self.assertEqual(len(headers.keys()), 2)

        # ironic microversion, specified service type
        headers = {}
        client_session.Session._set_microversion_headers(
            headers, '2.30', 'baremetal', None)
        self.assertEqual(headers['OpenStack-API-Version'], 'baremetal 2.30')
        self.assertEqual(headers['X-OpenStack-Ironic-API-Version'], '2.30')
        self.assertEqual(len(headers.keys()), 2)

        # volumev2 service-type - volume microversion
        headers = {}
        client_session.Session._set_microversion_headers(
            headers, (2, 30), None, {'service_type': 'volumev2'})
        self.assertEqual(headers['OpenStack-API-Version'], 'volume 2.30')
        self.assertEqual(len(headers.keys()), 1)

        # block-storage service-type - volume microversion
        headers = {}
        client_session.Session._set_microversion_headers(
            headers, (2, 30), None, {'service_type': 'block-storage'})
        self.assertEqual(headers['OpenStack-API-Version'], 'volume 2.30')
        self.assertEqual(len(headers.keys()), 1)

        # Headers already exist - no change
        headers = {
            'OpenStack-API-Version': 'compute 2.30',
            'X-OpenStack-Nova-API-Version': '2.30',
        }
        client_session.Session._set_microversion_headers(
            headers, (2, 31), None, {'service_type': 'volume'})
        self.assertEqual(headers['OpenStack-API-Version'], 'compute 2.30')
        self.assertEqual(headers['X-OpenStack-Nova-API-Version'], '2.30')

        # Can't specify a 'M.latest' microversion
        self.assertRaises(TypeError,
                          client_session.Session._set_microversion_headers,
                          {}, '2.latest', 'service_type', None)
        self.assertRaises(TypeError,
                          client_session.Session._set_microversion_headers,
                          {}, (2, discover.LATEST), 'service_type', None)

        # Normalization error
        self.assertRaises(TypeError,
                          client_session.Session._set_microversion_headers,
                          {}, 'bogus', 'service_type', None)

        # No service type in param or endpoint filter
        self.assertRaises(TypeError,
                          client_session.Session._set_microversion_headers,
                          {}, (2, 30), None, None)
        self.assertRaises(TypeError,
                          client_session.Session._set_microversion_headers,
                          {}, (2, 30), None, {'no_service_type': 'here'})

    def test_microversion(self):
        # microversion not specified
        session = client_session.Session()
        self.stub_url('GET', text='response')
        resp = session.get(self.TEST_URL)

        self.assertTrue(resp.ok)
        self.assertRequestNotInHeader('OpenStack-API-Version')

        session = client_session.Session()
        self.stub_url('GET', text='response')
        resp = session.get(self.TEST_URL, microversion='2.30',
                           microversion_service_type='compute',
                           endpoint_filter={'endpoint': 'filter'})

        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('OpenStack-API-Version', 'compute 2.30')
        self.assertRequestHeaderEqual('X-OpenStack-Nova-API-Version', '2.30')

    def test_user_agent(self):
        session = client_session.Session()
        self.stub_url('GET', text='response')
        resp = session.get(self.TEST_URL)

        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual(
            'User-Agent',
            '%s %s' % ("run.py", client_session.DEFAULT_USER_AGENT))

        custom_agent = 'custom-agent/1.0'
        session = client_session.Session(user_agent=custom_agent)
        self.stub_url('GET', text='response')
        resp = session.get(self.TEST_URL)

        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual(
            'User-Agent',
            '%s %s' % (custom_agent, client_session.DEFAULT_USER_AGENT))

        resp = session.get(self.TEST_URL, headers={'User-Agent': 'new-agent'})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'new-agent')

        resp = session.get(self.TEST_URL, headers={'User-Agent': 'new-agent'},
                           user_agent='overrides-agent')
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'overrides-agent')

        # If sys.argv is an empty list, then doesn't fail.
        with mock.patch.object(sys, 'argv', []):
            session = client_session.Session()
            resp = session.get(self.TEST_URL)
            self.assertTrue(resp.ok)
            self.assertRequestHeaderEqual(
                'User-Agent',
                client_session.DEFAULT_USER_AGENT)

        # If sys.argv[0] is an empty string, then doesn't fail.
        with mock.patch.object(sys, 'argv', ['']):
            session = client_session.Session()
            resp = session.get(self.TEST_URL)
            self.assertTrue(resp.ok)
            self.assertRequestHeaderEqual(
                'User-Agent',
                client_session.DEFAULT_USER_AGENT)

    def test_http_session_opts(self):
        session = client_session.Session(cert='cert.pem', timeout=5,
                                         verify='certs')

        FAKE_RESP = utils.TestResponse({'status_code': 200, 'text': 'resp'})
        RESP = mock.Mock(return_value=FAKE_RESP)

        with mock.patch.object(session.session, 'request', RESP) as mocked:
            session.post(self.TEST_URL, data='value')

            mock_args, mock_kwargs = mocked.call_args

            self.assertEqual(mock_args[0], 'POST')
            self.assertEqual(mock_args[1], self.TEST_URL)
            self.assertEqual(mock_kwargs['data'], 'value')
            self.assertEqual(mock_kwargs['cert'], 'cert.pem')
            self.assertEqual(mock_kwargs['verify'], 'certs')
            self.assertEqual(mock_kwargs['timeout'], 5)

    def test_not_found(self):
        session = client_session.Session()
        self.stub_url('GET', status_code=404)
        self.assertRaises(exceptions.NotFound, session.get, self.TEST_URL)

    def test_server_error(self):
        session = client_session.Session()
        self.stub_url('GET', status_code=500)
        self.assertRaises(exceptions.InternalServerError,
                          session.get, self.TEST_URL)

    def test_session_debug_output(self):
        """Test request and response headers in debug logs.

        in order to redact secure headers while debug is true.
        """
        session = client_session.Session(verify=False)
        headers = {'HEADERA': 'HEADERVALB',
                   'Content-Type': 'application/json'}
        security_headers = {'Authorization': uuid.uuid4().hex,
                            'X-Auth-Token': uuid.uuid4().hex,
                            'X-Subject-Token': uuid.uuid4().hex,
                            'X-Service-Token': uuid.uuid4().hex}
        body = '{"a": "b"}'
        data = '{"c": "d"}'
        all_headers = dict(
            itertools.chain(headers.items(), security_headers.items()))
        self.stub_url('POST', text=body, headers=all_headers)
        resp = session.post(self.TEST_URL, headers=all_headers, data=data)
        self.assertEqual(resp.status_code, 200)

        self.assertIn('curl', self.logger.output)
        self.assertIn('POST', self.logger.output)
        self.assertIn('--insecure', self.logger.output)
        self.assertIn(body, self.logger.output)
        self.assertIn("'%s'" % data, self.logger.output)

        for k, v in headers.items():
            self.assertIn(k, self.logger.output)
            self.assertIn(v, self.logger.output)

        # Assert that response headers contains actual values and
        # only debug logs has been masked
        for k, v in security_headers.items():
            self.assertIn('%s: {SHA256}' % k, self.logger.output)
            self.assertEqual(v, resp.headers[k])
            self.assertNotIn(v, self.logger.output)

    def test_session_debug_output_logs_openstack_request_id(self):
        """Test x-openstack-request-id is logged in debug logs."""
        def get_response(log=True):
            session = client_session.Session(verify=False)
            endpoint_filter = {'service_name': 'Identity'}
            headers = {'X-OpenStack-Request-Id': 'req-1234'}
            body = 'BODYRESPONSE'
            data = 'BODYDATA'
            all_headers = dict(itertools.chain(headers.items()))
            self.stub_url('POST', text=body, headers=all_headers)
            resp = session.post(self.TEST_URL, endpoint_filter=endpoint_filter,
                                headers=all_headers, data=data, log=log)
            return resp

        # if log is disabled then request-id is not logged in debug logs
        resp = get_response(log=False)
        self.assertEqual(resp.status_code, 200)

        expected_log = ('POST call to Identity for %s used request '
                        'id req-1234' % self.TEST_URL)
        self.assertNotIn(expected_log, self.logger.output)

        # if log is enabled then request-id is logged in debug logs
        resp = get_response()
        self.assertEqual(resp.status_code, 200)
        self.assertIn(expected_log, self.logger.output)

    def test_logs_failed_output(self):
        """Test that output is logged even for failed requests."""
        session = client_session.Session()
        body = {uuid.uuid4().hex: uuid.uuid4().hex}

        self.stub_url('GET', json=body, status_code=400,
                      headers={'Content-Type': 'application/json'})
        resp = session.get(self.TEST_URL, raise_exc=False)

        self.assertEqual(resp.status_code, 400)
        self.assertIn(list(body.keys())[0], self.logger.output)
        self.assertIn(list(body.values())[0], self.logger.output)

    def test_logging_body_only_for_specified_content_types(self):
        """Verify response body is only logged in specific content types.

        Response bodies are logged only when the response's Content-Type header
        is set to application/json. This prevents us to get an unexpected
        MemoryError when reading arbitrary responses, such as streams.
        """
        OMITTED_BODY = ('Omitted, Content-Type is set to %s. Only '
                        'application/json responses have their bodies logged.')
        session = client_session.Session(verify=False)

        # Content-Type is not set
        body = json.dumps({'token': {'id': '...'}})
        self.stub_url('POST', text=body)
        session.post(self.TEST_URL)
        self.assertNotIn(body, self.logger.output)
        self.assertIn(OMITTED_BODY % None, self.logger.output)

        # Content-Type is set to text/xml
        body = '<token><id>...</id></token>'
        self.stub_url('POST', text=body, headers={'Content-Type': 'text/xml'})
        session.post(self.TEST_URL)
        self.assertNotIn(body, self.logger.output)
        self.assertIn(OMITTED_BODY % 'text/xml', self.logger.output)

        # Content-Type is set to application/json
        body = json.dumps({'token': {'id': '...'}})
        self.stub_url('POST', text=body,
                      headers={'Content-Type': 'application/json'})
        session.post(self.TEST_URL)
        self.assertIn(body, self.logger.output)
        self.assertNotIn(OMITTED_BODY % 'application/json', self.logger.output)

        # Content-Type is set to application/json; charset=UTF-8
        body = json.dumps({'token': {'id': '...'}})
        self.stub_url(
            'POST', text=body,
            headers={'Content-Type': 'application/json; charset=UTF-8'})
        session.post(self.TEST_URL)
        self.assertIn(body, self.logger.output)
        self.assertNotIn(OMITTED_BODY % 'application/json; charset=UTF-8',
                         self.logger.output)

    def test_logging_cacerts(self):
        path_to_certs = '/path/to/certs'
        session = client_session.Session(verify=path_to_certs)

        self.stub_url('GET', text='text')
        session.get(self.TEST_URL)

        self.assertIn('--cacert', self.logger.output)
        self.assertIn(path_to_certs, self.logger.output)

    def _connect_retries_check(self, session, expected_retries=0,
                               call_args=None):
        call_args = call_args or {}

        self.stub_url('GET', exc=requests.exceptions.Timeout())

        call_args['url'] = self.TEST_URL

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.ConnectTimeout,
                              session.get,
                              **call_args)

            self.assertEqual(expected_retries, m.call_count)
            # 3 retries finishing with 2.0 means 0.5, 1.0 and 2.0
            m.assert_called_with(2.0)

        # we count retries so there will be one initial request + 3 retries
        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(expected_retries + 1))

    def test_session_connect_retries(self):
        retries = 3
        session = client_session.Session(connect_retries=retries)
        self._connect_retries_check(session=session, expected_retries=retries)

    def test_call_args_connect_retries_session_init(self):
        session = client_session.Session()
        retries = 3
        call_args = {'connect_retries': retries}
        self._connect_retries_check(session=session,
                                    expected_retries=retries,
                                    call_args=call_args)

    def test_call_args_connect_retries_overrides_session_retries(self):
        session_retries = 6
        call_arg_retries = 3
        call_args = {'connect_retries': call_arg_retries}
        session = client_session.Session(connect_retries=session_retries)
        self._connect_retries_check(session=session,
                                    expected_retries=call_arg_retries,
                                    call_args=call_args)

    def test_override_session_connect_retries_for_request(self):
        session_retries = 1
        session = client_session.Session(connect_retries=session_retries)

        self.stub_url('GET', exc=requests.exceptions.Timeout())
        call_args = {'connect_retries': 0}

        with mock.patch('time.sleep') as m:
            self.assertRaises(
                exceptions.ConnectTimeout,
                session.request,
                self.TEST_URL,
                'GET',
                **call_args
            )

            self.assertEqual(0, m.call_count)

    def test_connect_retries_interval_limit(self):
        self.stub_url('GET', exc=requests.exceptions.Timeout())

        session = client_session.Session()
        retries = 20

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.ConnectTimeout,
                              session.get,
                              self.TEST_URL, connect_retries=retries)

            self.assertEqual(retries, m.call_count)
            # The interval maxes out at 60
            m.assert_called_with(60.0)

        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(retries + 1))

    def test_connect_retries_fixed_delay(self):
        self.stub_url('GET', exc=requests.exceptions.Timeout())

        session = client_session.Session()
        retries = 3

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.ConnectTimeout,
                              session.get,
                              self.TEST_URL, connect_retries=retries,
                              connect_retry_delay=0.5)

            self.assertEqual(retries, m.call_count)
            m.assert_has_calls([mock.call(0.5)] * retries)

        # we count retries so there will be one initial request + 3 retries
        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(retries + 1))

    def test_http_503_retries(self):
        self.stub_url('GET', status_code=503)

        session = client_session.Session()
        retries = 3

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.ServiceUnavailable,
                              session.get,
                              self.TEST_URL, status_code_retries=retries)

            self.assertEqual(retries, m.call_count)
            # 3 retries finishing with 2.0 means 0.5, 1.0 and 2.0
            m.assert_called_with(2.0)

        # we count retries so there will be one initial request + 3 retries
        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(retries + 1))

    def test_http_status_retries(self):
        self.stub_url('GET', status_code=409)

        session = client_session.Session()
        retries = 3

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.Conflict,
                              session.get,
                              self.TEST_URL, status_code_retries=retries,
                              retriable_status_codes=[503, 409])

            self.assertEqual(retries, m.call_count)
            # 3 retries finishing with 2.0 means 0.5, 1.0 and 2.0
            m.assert_called_with(2.0)

        # we count retries so there will be one initial request + 3 retries
        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(retries + 1))

    def test_http_status_retries_another_code(self):
        self.stub_url('GET', status_code=404)

        session = client_session.Session()
        retries = 3

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.NotFound,
                              session.get,
                              self.TEST_URL, status_code_retries=retries,
                              retriable_status_codes=[503, 409])

            self.assertFalse(m.called)

        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(1))

    def test_http_status_retries_fixed_delay(self):
        self.stub_url('GET', status_code=409)

        session = client_session.Session()
        retries = 3

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.Conflict,
                              session.get,
                              self.TEST_URL, status_code_retries=retries,
                              status_code_retry_delay=0.5,
                              retriable_status_codes=[503, 409])

            self.assertEqual(retries, m.call_count)
            m.assert_has_calls([mock.call(0.5)] * retries)

        # we count retries so there will be one initial request + 3 retries
        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(retries + 1))

    def test_http_status_retries_inverval_limit(self):
        self.stub_url('GET', status_code=409)

        session = client_session.Session()
        retries = 20

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.Conflict,
                              session.get,
                              self.TEST_URL, status_code_retries=retries,
                              retriable_status_codes=[503, 409])

            self.assertEqual(retries, m.call_count)
            # The interval maxes out at 60
            m.assert_called_with(60.0)

        # we count retries so there will be one initial request + 3 retries
        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(retries + 1))

    def test_uses_tcp_keepalive_by_default(self):
        session = client_session.Session()
        requests_session = session.session
        self.assertIsInstance(requests_session.adapters['http://'],
                              client_session.TCPKeepAliveAdapter)
        self.assertIsInstance(requests_session.adapters['https://'],
                              client_session.TCPKeepAliveAdapter)

    def test_does_not_set_tcp_keepalive_on_custom_sessions(self):
        mock_session = mock.Mock()
        client_session.Session(session=mock_session)
        self.assertFalse(mock_session.mount.called)

    def test_ssl_error_message(self):
        error = uuid.uuid4().hex

        self.stub_url('GET', exc=requests.exceptions.SSLError(error))
        session = client_session.Session()

        # The exception should contain the URL and details about the SSL error
        msg = 'SSL exception connecting to %(url)s: %(error)s' % {
            'url': self.TEST_URL, 'error': error}
        self.assertRaisesRegex(exceptions.SSLError,
                               msg,
                               session.get,
                               self.TEST_URL)

    def test_json_content_type(self):
        session = client_session.Session()
        self.stub_url('POST', text='response')
        resp = session.post(
            self.TEST_URL,
            json=[{'op': 'replace',
                   'path': '/name',
                   'value': 'new_name'}],
            headers={'Content-Type': 'application/json-patch+json'})

        self.assertEqual('POST', self.requests_mock.last_request.method)
        self.assertEqual(resp.text, 'response')
        self.assertTrue(resp.ok)
        self.assertRequestBodyIs(
            json=[{'op': 'replace',
                   'path': '/name',
                   'value': 'new_name'}])
        self.assertContentTypeIs('application/json-patch+json')

    def test_api_sig_error_message_single(self):
        title = 'this error is bogus!'
        detail = 'it is a totally made up error'
        error_message = {
            'errors': [
                {
                    'request_id': uuid.uuid4().hex,
                    'code': 'phoney.bologna.error',
                    'status': 500,
                    'title': title,
                    'detail': detail,
                    'links': [
                        {
                            'rel': 'help',
                            'href': 'https://openstack.org'
                        }
                    ]
                }
            ]
        }
        payload = json.dumps(error_message)
        self.stub_url('GET', status_code=9000, text=payload,
                      headers={'Content-Type': 'application/json'})
        session = client_session.Session()

        # The exception should contain the information from the error response
        msg = '{} (HTTP 9000)'.format(title)
        try:
            session.get(self.TEST_URL)
        except exceptions.HttpError as ex:
            self.assertEqual(ex.message, msg)
            self.assertEqual(ex.details, detail)

    def test_api_sig_error_message_multiple(self):
        title = 'this error is the first error!'
        detail = 'it is a totally made up error'
        error_message = {
            'errors': [
                {
                    'request_id': uuid.uuid4().hex,
                    'code': 'phoney.bologna.error',
                    'status': 500,
                    'title': title,
                    'detail': detail,
                    'links': [
                        {
                            'rel': 'help',
                            'href': 'https://openstack.org'
                        }
                    ]
                },
                {
                    'request_id': uuid.uuid4().hex,
                    'code': 'phoney.bologna.error',
                    'status': 500,
                    'title': 'some other error',
                    'detail': detail,
                    'links': [
                        {
                            'rel': 'help',
                            'href': 'https://openstack.org'
                        }
                    ]
                }
            ]
        }
        payload = json.dumps(error_message)
        self.stub_url('GET', status_code=9000, text=payload,
                      headers={'Content-Type': 'application/json'})
        session = client_session.Session()

        # The exception should contain the information from the error response
        msg = ('Multiple error responses, showing first only: {} (HTTP 9000)'
               .format(title))
        try:
            session.get(self.TEST_URL)
        except exceptions.HttpError as ex:
            self.assertEqual(ex.message, msg)
            self.assertEqual(ex.details, detail)

    def test_api_sig_error_message_empty(self):
        error_message = {
            'errors': [
            ]
        }
        payload = json.dumps(error_message)
        self.stub_url('GET', status_code=9000, text=payload,
                      headers={'Content-Type': 'application/json'})
        session = client_session.Session()

        # The exception should contain the information from the error response
        msg = 'HTTP Error (HTTP 9000)'

        try:
            session.get(self.TEST_URL)
        except exceptions.HttpError as ex:
            self.assertEqual(ex.message, msg)
            self.assertIsNone(ex.details)

    def test_error_message_unknown_schema(self):
        error_message = 'Uh oh, things went bad!'
        payload = json.dumps(error_message)
        self.stub_url('GET', status_code=9000, text=payload,
                      headers={'Content-Type': 'application/json'})
        session = client_session.Session()

        msg = 'Unrecognized schema in response body. (HTTP 9000)'
        try:
            session.get(self.TEST_URL)
        except exceptions.HttpError as ex:
            self.assertEqual(ex.message, msg)


class RedirectTests(utils.TestCase):

    REDIRECT_CHAIN = ['http://myhost:3445/',
                      'http://anotherhost:6555/',
                      'http://thirdhost/',
                      'http://finaldestination:55/']

    DEFAULT_REDIRECT_BODY = 'Redirect'
    DEFAULT_RESP_BODY = 'Found'

    def setup_redirects(self, method='GET', status_code=305,
                        redirect_kwargs={}, final_kwargs={}):
        redirect_kwargs.setdefault('text', self.DEFAULT_REDIRECT_BODY)

        for s, d in zip(self.REDIRECT_CHAIN, self.REDIRECT_CHAIN[1:]):
            self.requests_mock.register_uri(method, s, status_code=status_code,
                                            headers={'Location': d},
                                            **redirect_kwargs)

        final_kwargs.setdefault('status_code', 200)
        final_kwargs.setdefault('text', self.DEFAULT_RESP_BODY)
        self.requests_mock.register_uri(method, self.REDIRECT_CHAIN[-1],
                                        **final_kwargs)

    def assertResponse(self, resp):
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text, self.DEFAULT_RESP_BODY)

    def test_basic_get(self):
        session = client_session.Session()
        self.setup_redirects()
        resp = session.get(self.REDIRECT_CHAIN[-2])
        self.assertResponse(resp)

    def test_basic_post_keeps_correct_method(self):
        session = client_session.Session()
        self.setup_redirects(method='POST', status_code=301)
        resp = session.post(self.REDIRECT_CHAIN[-2])
        self.assertResponse(resp)

    def test_redirect_forever(self):
        session = client_session.Session(redirect=True)
        self.setup_redirects()
        resp = session.get(self.REDIRECT_CHAIN[0])
        self.assertResponse(resp)
        self.assertTrue(len(resp.history), len(self.REDIRECT_CHAIN))

    def test_no_redirect(self):
        session = client_session.Session(redirect=False)
        self.setup_redirects()
        resp = session.get(self.REDIRECT_CHAIN[0])
        self.assertEqual(resp.status_code, 305)
        self.assertEqual(resp.url, self.REDIRECT_CHAIN[0])

    def test_redirect_limit(self):
        self.setup_redirects()
        for i in (1, 2):
            session = client_session.Session(redirect=i)
            resp = session.get(self.REDIRECT_CHAIN[0])
            self.assertEqual(resp.status_code, 305)
            self.assertEqual(resp.url, self.REDIRECT_CHAIN[i])
            self.assertEqual(resp.text, self.DEFAULT_REDIRECT_BODY)

    def test_history_matches_requests(self):
        self.setup_redirects(status_code=301)
        session = client_session.Session(redirect=True)
        req_resp = requests.get(self.REDIRECT_CHAIN[0],
                                allow_redirects=True)

        ses_resp = session.get(self.REDIRECT_CHAIN[0])

        self.assertEqual(len(req_resp.history), len(ses_resp.history))

        for r, s in zip(req_resp.history, ses_resp.history):
            self.assertEqual(r.url, s.url)
            self.assertEqual(r.status_code, s.status_code)

    def test_permanent_redirect_308(self):
        session = client_session.Session()
        self.setup_redirects(status_code=308)
        resp = session.get(self.REDIRECT_CHAIN[-2])
        self.assertResponse(resp)


class AuthPlugin(plugin.BaseAuthPlugin):
    """Very simple debug authentication plugin.

    Takes Parameters such that it can throw exceptions at the right times.
    """

    TEST_TOKEN = utils.TestCase.TEST_TOKEN
    TEST_USER_ID = 'aUser'
    TEST_PROJECT_ID = 'aProject'

    SERVICE_URLS = {
        'identity': {'public': 'http://identity-public:1111/v2.0',
                     'admin': 'http://identity-admin:1111/v2.0'},
        'compute': {'public': 'http://compute-public:2222/v1.0',
                    'admin': 'http://compute-admin:2222/v1.0'},
        'image': {'public': 'http://image-public:3333/v2.0',
                  'admin': 'http://image-admin:3333/v2.0'}
    }

    def __init__(self, token=TEST_TOKEN, invalidate=True):
        self.token = token
        self._invalidate = invalidate

    def get_token(self, session):
        return self.token

    def get_endpoint(self, session, service_type=None, interface=None,
                     **kwargs):
        try:
            return self.SERVICE_URLS[service_type][interface]
        except (KeyError, AttributeError):
            return None

    def invalidate(self):
        return self._invalidate

    def get_user_id(self, session):
        return self.TEST_USER_ID

    def get_project_id(self, session):
        return self.TEST_PROJECT_ID


class CalledAuthPlugin(plugin.BaseAuthPlugin):

    ENDPOINT = 'http://fakeendpoint/'
    TOKEN = utils.TestCase.TEST_TOKEN
    USER_ID = uuid.uuid4().hex
    PROJECT_ID = uuid.uuid4().hex

    def __init__(self, invalidate=True):
        self.get_token_called = False
        self.get_endpoint_called = False
        self.endpoint_arguments = {}
        self.invalidate_called = False
        self.get_project_id_called = False
        self.get_user_id_called = False
        self._invalidate = invalidate

    def get_token(self, session):
        self.get_token_called = True
        return self.TOKEN

    def get_endpoint(self, session, **kwargs):
        self.get_endpoint_called = True
        self.endpoint_arguments = kwargs
        return self.ENDPOINT

    def invalidate(self):
        self.invalidate_called = True
        return self._invalidate

    def get_project_id(self, session, **kwargs):
        self.get_project_id_called = True
        return self.PROJECT_ID

    def get_user_id(self, session, **kwargs):
        self.get_user_id_called = True
        return self.USER_ID


class SessionAuthTests(utils.TestCase):

    TEST_URL = 'http://127.0.0.1:5000/'
    TEST_JSON = {'hello': 'world'}

    def stub_service_url(self, service_type, interface, path,
                         method='GET', **kwargs):
        base_url = AuthPlugin.SERVICE_URLS[service_type][interface]
        uri = "%s/%s" % (base_url.rstrip('/'), path.lstrip('/'))

        self.requests_mock.register_uri(method, uri, **kwargs)

    def test_auth_plugin_default_with_plugin(self):
        self.stub_url('GET', base_url=self.TEST_URL, json=self.TEST_JSON)

        # if there is an auth_plugin then it should default to authenticated
        auth = AuthPlugin()
        sess = client_session.Session(auth=auth)
        resp = sess.get(self.TEST_URL)
        self.assertEqual(resp.json(), self.TEST_JSON)

        self.assertRequestHeaderEqual('X-Auth-Token', AuthPlugin.TEST_TOKEN)

    def test_auth_plugin_disable(self):
        self.stub_url('GET', base_url=self.TEST_URL, json=self.TEST_JSON)

        auth = AuthPlugin()
        sess = client_session.Session(auth=auth)
        resp = sess.get(self.TEST_URL, authenticated=False)
        self.assertEqual(resp.json(), self.TEST_JSON)

        self.assertRequestHeaderEqual('X-Auth-Token', None)

    def test_object_delete(self):
        auth = AuthPlugin()
        sess = client_session.Session(auth=auth)
        mock_close = mock.Mock()
        sess._session.close = mock_close
        del sess
        self.assertEqual(1, mock_close.call_count)

    def test_service_type_urls(self):
        service_type = 'compute'
        interface = 'public'
        path = '/instances'
        status = 200
        body = 'SUCCESS'

        self.stub_service_url(service_type=service_type,
                              interface=interface,
                              path=path,
                              status_code=status,
                              text=body)

        sess = client_session.Session(auth=AuthPlugin())
        resp = sess.get(path,
                        endpoint_filter={'service_type': service_type,
                                         'interface': interface})

        self.assertEqual(self.requests_mock.last_request.url,
                         AuthPlugin.SERVICE_URLS['compute']['public'] + path)
        self.assertEqual(resp.text, body)
        self.assertEqual(resp.status_code, status)

    def test_service_url_raises_if_no_auth_plugin(self):
        sess = client_session.Session()
        self.assertRaises(exceptions.MissingAuthPlugin,
                          sess.get, '/path',
                          endpoint_filter={'service_type': 'compute',
                                           'interface': 'public'})

    def test_service_url_raises_if_no_url_returned(self):
        sess = client_session.Session(auth=AuthPlugin())
        self.assertRaises(exceptions.EndpointNotFound,
                          sess.get, '/path',
                          endpoint_filter={'service_type': 'unknown',
                                           'interface': 'public'})

    def test_raises_exc_only_when_asked(self):
        # A request that returns a HTTP error should by default raise an
        # exception by default, if you specify raise_exc=False then it will not
        self.requests_mock.get(self.TEST_URL, status_code=401)

        sess = client_session.Session()
        self.assertRaises(exceptions.Unauthorized, sess.get, self.TEST_URL)

        resp = sess.get(self.TEST_URL, raise_exc=False)
        self.assertEqual(401, resp.status_code)

    def test_passed_auth_plugin(self):
        passed = CalledAuthPlugin()
        sess = client_session.Session()

        self.requests_mock.get(CalledAuthPlugin.ENDPOINT + 'path',
                               status_code=200)
        endpoint_filter = {'service_type': 'identity'}

        # no plugin with authenticated won't work
        self.assertRaises(exceptions.MissingAuthPlugin, sess.get, 'path',
                          authenticated=True)

        # no plugin with an endpoint filter won't work
        self.assertRaises(exceptions.MissingAuthPlugin, sess.get, 'path',
                          authenticated=False, endpoint_filter=endpoint_filter)

        resp = sess.get('path', auth=passed, endpoint_filter=endpoint_filter)

        self.assertEqual(200, resp.status_code)
        self.assertTrue(passed.get_endpoint_called)
        self.assertTrue(passed.get_token_called)

    def test_passed_auth_plugin_overrides(self):
        fixed = CalledAuthPlugin()
        passed = CalledAuthPlugin()

        sess = client_session.Session(fixed)

        self.requests_mock.get(CalledAuthPlugin.ENDPOINT + 'path',
                               status_code=200)

        resp = sess.get('path', auth=passed,
                        endpoint_filter={'service_type': 'identity'})

        self.assertEqual(200, resp.status_code)
        self.assertTrue(passed.get_endpoint_called)
        self.assertTrue(passed.get_token_called)
        self.assertFalse(fixed.get_endpoint_called)
        self.assertFalse(fixed.get_token_called)

    def test_requests_auth_plugin(self):
        sess = client_session.Session()
        requests_auth = RequestsAuth()

        self.requests_mock.get(self.TEST_URL, text='resp')

        sess.get(self.TEST_URL, requests_auth=requests_auth)
        last = self.requests_mock.last_request

        self.assertEqual(requests_auth.header_val,
                         last.headers[requests_auth.header_name])
        self.assertTrue(requests_auth.called)

    def test_reauth_called(self):
        auth = CalledAuthPlugin(invalidate=True)
        sess = client_session.Session(auth=auth)

        self.requests_mock.get(self.TEST_URL,
                               [{'text': 'Failed', 'status_code': 401},
                                {'text': 'Hello', 'status_code': 200}])

        # allow_reauth=True is the default
        resp = sess.get(self.TEST_URL, authenticated=True)

        self.assertEqual(200, resp.status_code)
        self.assertEqual('Hello', resp.text)
        self.assertTrue(auth.invalidate_called)

    def test_reauth_not_called(self):
        auth = CalledAuthPlugin(invalidate=True)
        sess = client_session.Session(auth=auth)

        self.requests_mock.get(self.TEST_URL,
                               [{'text': 'Failed', 'status_code': 401},
                                {'text': 'Hello', 'status_code': 200}])

        self.assertRaises(exceptions.Unauthorized, sess.get, self.TEST_URL,
                          authenticated=True, allow_reauth=False)
        self.assertFalse(auth.invalidate_called)

    def test_endpoint_override_overrides_filter(self):
        auth = CalledAuthPlugin()
        sess = client_session.Session(auth=auth)

        override_base = 'http://mytest/'
        path = 'path'
        override_url = override_base + path
        resp_text = uuid.uuid4().hex

        self.requests_mock.get(override_url, text=resp_text)

        resp = sess.get(path,
                        endpoint_override=override_base,
                        endpoint_filter={'service_type': 'identity'})

        self.assertEqual(resp_text, resp.text)
        self.assertEqual(override_url, self.requests_mock.last_request.url)

        self.assertTrue(auth.get_token_called)
        self.assertFalse(auth.get_endpoint_called)

        self.assertFalse(auth.get_user_id_called)
        self.assertFalse(auth.get_project_id_called)

    def test_endpoint_override_ignore_full_url(self):
        auth = CalledAuthPlugin()
        sess = client_session.Session(auth=auth)

        path = 'path'
        url = self.TEST_URL + path

        resp_text = uuid.uuid4().hex
        self.requests_mock.get(url, text=resp_text)

        resp = sess.get(url,
                        endpoint_override='http://someother.url',
                        endpoint_filter={'service_type': 'identity'})

        self.assertEqual(resp_text, resp.text)
        self.assertEqual(url, self.requests_mock.last_request.url)

        self.assertTrue(auth.get_token_called)
        self.assertFalse(auth.get_endpoint_called)

        self.assertFalse(auth.get_user_id_called)
        self.assertFalse(auth.get_project_id_called)

    def test_endpoint_override_does_id_replacement(self):
        auth = CalledAuthPlugin()
        sess = client_session.Session(auth=auth)

        override_base = 'http://mytest/%(project_id)s/%(user_id)s'
        path = 'path'
        replacements = {'user_id': CalledAuthPlugin.USER_ID,
                        'project_id': CalledAuthPlugin.PROJECT_ID}
        override_url = override_base % replacements + '/' + path
        resp_text = uuid.uuid4().hex

        self.requests_mock.get(override_url, text=resp_text)

        resp = sess.get(path,
                        endpoint_override=override_base,
                        endpoint_filter={'service_type': 'identity'})

        self.assertEqual(resp_text, resp.text)
        self.assertEqual(override_url, self.requests_mock.last_request.url)

        self.assertTrue(auth.get_token_called)
        self.assertTrue(auth.get_user_id_called)
        self.assertTrue(auth.get_project_id_called)
        self.assertFalse(auth.get_endpoint_called)

    def test_endpoint_override_fails_to_replace_if_none(self):
        # The token_endpoint plugin doesn't know user_id or project_id
        auth = token_endpoint.Token(uuid.uuid4().hex, uuid.uuid4().hex)
        sess = client_session.Session(auth=auth)

        override_base = 'http://mytest/%(project_id)s'

        e = self.assertRaises(ValueError,
                              sess.get,
                              '/path',
                              endpoint_override=override_base,
                              endpoint_filter={'service_type': 'identity'})

        self.assertIn('project_id', str(e))
        override_base = 'http://mytest/%(user_id)s'

        e = self.assertRaises(ValueError,
                              sess.get,
                              '/path',
                              endpoint_override=override_base,
                              endpoint_filter={'service_type': 'identity'})
        self.assertIn('user_id', str(e))

    def test_endpoint_override_fails_to_do_unknown_replacement(self):
        auth = CalledAuthPlugin()
        sess = client_session.Session(auth=auth)

        override_base = 'http://mytest/%(unknown_id)s'

        e = self.assertRaises(AttributeError,
                              sess.get,
                              '/path',
                              endpoint_override=override_base,
                              endpoint_filter={'service_type': 'identity'})
        self.assertIn('unknown_id', str(e))

    def test_user_and_project_id(self):
        auth = AuthPlugin()
        sess = client_session.Session(auth=auth)

        self.assertEqual(auth.TEST_USER_ID, sess.get_user_id())
        self.assertEqual(auth.TEST_PROJECT_ID, sess.get_project_id())

    def test_logger_object_passed(self):
        logger = logging.getLogger(uuid.uuid4().hex)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        io = six.StringIO()
        handler = logging.StreamHandler(io)
        logger.addHandler(handler)

        auth = AuthPlugin()
        sess = client_session.Session(auth=auth)
        response = {uuid.uuid4().hex: uuid.uuid4().hex}

        self.stub_url('GET',
                      json=response,
                      headers={'Content-Type': 'application/json'})

        resp = sess.get(self.TEST_URL, logger=logger)

        self.assertEqual(response, resp.json())
        output = io.getvalue()

        self.assertIn(self.TEST_URL, output)
        self.assertIn(list(response.keys())[0], output)
        self.assertIn(list(response.values())[0], output)

        self.assertNotIn(list(response.keys())[0], self.logger.output)
        self.assertNotIn(list(response.values())[0], self.logger.output)

    def test_split_loggers(self):

        def get_logger_io(name):
            logger_name = 'keystoneauth.session.{name}'.format(name=name)
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)

            io = six.StringIO()
            handler = logging.StreamHandler(io)
            logger.addHandler(handler)
            return io

        io = {}
        for name in ('request', 'body', 'response', 'request-id'):
            io[name] = get_logger_io(name)

        auth = AuthPlugin()
        sess = client_session.Session(auth=auth, split_loggers=True)
        response_key = uuid.uuid4().hex
        response_val = uuid.uuid4().hex
        response = {response_key: response_val}
        request_id = uuid.uuid4().hex

        self.stub_url(
            'GET',
            json=response,
            headers={
                'Content-Type': 'application/json',
                'X-OpenStack-Request-ID': request_id,
            })

        resp = sess.get(
            self.TEST_URL,
            headers={
                encodeutils.safe_encode('x-bytes-header'):
                encodeutils.safe_encode('bytes-value')
            })

        self.assertEqual(response, resp.json())

        request_output = io['request'].getvalue().strip()
        response_output = io['response'].getvalue().strip()
        body_output = io['body'].getvalue().strip()
        id_output = io['request-id'].getvalue().strip()

        self.assertIn('curl -g -i -X GET {url}'.format(url=self.TEST_URL),
                      request_output)
        self.assertIn('-H "x-bytes-header: bytes-value"', request_output)
        self.assertEqual('[200] Content-Type: application/json '
                         'X-OpenStack-Request-ID: '
                         '{id}'.format(id=request_id), response_output)
        self.assertEqual(
            'GET call to {url} used request id {id}'.format(
                url=self.TEST_URL, id=request_id),
            id_output)
        self.assertEqual(
            '{{"{key}": "{val}"}}'.format(
                key=response_key, val=response_val),
            body_output)

    def test_collect_timing(self):
        auth = AuthPlugin()
        sess = client_session.Session(auth=auth, collect_timing=True)
        response = {uuid.uuid4().hex: uuid.uuid4().hex}

        self.stub_url('GET',
                      json=response,
                      headers={'Content-Type': 'application/json'})

        resp = sess.get(self.TEST_URL)

        self.assertEqual(response, resp.json())
        timings = sess.get_timings()
        self.assertEqual(timings[0].method, 'GET')
        self.assertEqual(timings[0].url, self.TEST_URL)
        self.assertIsInstance(timings[0].elapsed, datetime.timedelta)
        sess.reset_timings()
        timings = sess.get_timings()
        self.assertEqual(len(timings), 0)


class AdapterTest(utils.TestCase):

    SERVICE_TYPE = uuid.uuid4().hex
    SERVICE_NAME = uuid.uuid4().hex
    INTERFACE = uuid.uuid4().hex
    REGION_NAME = uuid.uuid4().hex
    USER_AGENT = uuid.uuid4().hex
    VERSION = uuid.uuid4().hex
    ALLOW = {'allow_deprecated': False,
             'allow_experimental': True,
             'allow_unknown': True}

    TEST_URL = CalledAuthPlugin.ENDPOINT

    def _create_loaded_adapter(self, sess=None, auth=None):
        return adapter.Adapter(sess or client_session.Session(),
                               auth=auth or CalledAuthPlugin(),
                               service_type=self.SERVICE_TYPE,
                               service_name=self.SERVICE_NAME,
                               interface=self.INTERFACE,
                               region_name=self.REGION_NAME,
                               user_agent=self.USER_AGENT,
                               version=self.VERSION,
                               allow=self.ALLOW)

    def _verify_endpoint_called(self, adpt):
        self.assertEqual(self.SERVICE_TYPE,
                         adpt.auth.endpoint_arguments['service_type'])
        self.assertEqual(self.SERVICE_NAME,
                         adpt.auth.endpoint_arguments['service_name'])
        self.assertEqual(self.INTERFACE,
                         adpt.auth.endpoint_arguments['interface'])
        self.assertEqual(self.REGION_NAME,
                         adpt.auth.endpoint_arguments['region_name'])
        self.assertEqual(self.VERSION,
                         adpt.auth.endpoint_arguments['version'])

    def test_setting_variables_on_request(self):
        response = uuid.uuid4().hex
        self.stub_url('GET', text=response)
        adpt = self._create_loaded_adapter()
        resp = adpt.get('/')
        self.assertEqual(resp.text, response)

        self._verify_endpoint_called(adpt)
        self.assertEqual(self.ALLOW,
                         adpt.auth.endpoint_arguments['allow'])
        self.assertTrue(adpt.auth.get_token_called)
        self.assertRequestHeaderEqual('User-Agent', self.USER_AGENT)

    def test_setting_global_id_on_request(self):
        global_id_adpt = "req-%s" % uuid.uuid4()
        global_id_req = "req-%s" % uuid.uuid4()
        response = uuid.uuid4().hex
        self.stub_url('GET', text=response)

        def mk_adpt(**kwargs):
            return adapter.Adapter(client_session.Session(),
                                   auth=CalledAuthPlugin(),
                                   service_type=self.SERVICE_TYPE,
                                   service_name=self.SERVICE_NAME,
                                   interface=self.INTERFACE,
                                   region_name=self.REGION_NAME,
                                   user_agent=self.USER_AGENT,
                                   version=self.VERSION,
                                   allow=self.ALLOW,
                                   **kwargs)

        # No global_request_id
        adpt = mk_adpt()
        resp = adpt.get('/')
        self.assertEqual(resp.text, response)

        self._verify_endpoint_called(adpt)
        self.assertEqual(self.ALLOW,
                         adpt.auth.endpoint_arguments['allow'])
        self.assertTrue(adpt.auth.get_token_called)
        self.assertRequestHeaderEqual('X-OpenStack-Request-ID', None)

        # global_request_id only on the request
        adpt.get('/', global_request_id=global_id_req)
        self.assertRequestHeaderEqual('X-OpenStack-Request-ID', global_id_req)

        # global_request_id only on the adapter
        adpt = mk_adpt(global_request_id=global_id_adpt)
        adpt.get('/')
        self.assertRequestHeaderEqual('X-OpenStack-Request-ID', global_id_adpt)

        # global_request_id on the adapter *and* the request (the request takes
        # precedence)
        adpt.get('/', global_request_id=global_id_req)
        self.assertRequestHeaderEqual('X-OpenStack-Request-ID', global_id_req)

    def test_setting_variables_on_get_endpoint(self):
        adpt = self._create_loaded_adapter()
        url = adpt.get_endpoint()

        self.assertEqual(self.TEST_URL, url)
        self._verify_endpoint_called(adpt)

    def test_legacy_binding(self):
        key = uuid.uuid4().hex
        val = uuid.uuid4().hex
        response = json.dumps({key: val})

        self.stub_url('GET', text=response)

        auth = CalledAuthPlugin()
        sess = client_session.Session(auth=auth)
        adpt = adapter.LegacyJsonAdapter(sess,
                                         service_type=self.SERVICE_TYPE,
                                         user_agent=self.USER_AGENT)

        resp, body = adpt.get('/')
        self.assertEqual(self.SERVICE_TYPE,
                         auth.endpoint_arguments['service_type'])
        self.assertEqual(resp.text, response)
        self.assertEqual(val, body[key])

    def test_legacy_binding_non_json_resp(self):
        response = uuid.uuid4().hex
        self.stub_url('GET', text=response,
                      headers={'Content-Type': 'text/html'})

        auth = CalledAuthPlugin()
        sess = client_session.Session(auth=auth)
        adpt = adapter.LegacyJsonAdapter(sess,
                                         service_type=self.SERVICE_TYPE,
                                         user_agent=self.USER_AGENT)

        resp, body = adpt.get('/')
        self.assertEqual(self.SERVICE_TYPE,
                         auth.endpoint_arguments['service_type'])
        self.assertEqual(resp.text, response)
        self.assertIsNone(body)

    def test_methods(self):
        sess = client_session.Session()
        adpt = adapter.Adapter(sess)
        url = 'http://url'

        for method in ['get', 'head', 'post', 'put', 'patch', 'delete']:
            with mock.patch.object(adpt, 'request') as m:
                getattr(adpt, method)(url)
                m.assert_called_once_with(url, method.upper())

    def test_setting_endpoint_override(self):
        endpoint_override = 'http://overrideurl'
        path = '/path'
        endpoint_url = endpoint_override + path

        auth = CalledAuthPlugin()
        sess = client_session.Session(auth=auth)
        adpt = adapter.Adapter(sess, endpoint_override=endpoint_override)

        response = uuid.uuid4().hex
        self.requests_mock.get(endpoint_url, text=response)

        resp = adpt.get(path)

        self.assertEqual(response, resp.text)
        self.assertEqual(endpoint_url, self.requests_mock.last_request.url)

        self.assertEqual(endpoint_override, adpt.get_endpoint())

    def test_adapter_invalidate(self):
        auth = CalledAuthPlugin()
        sess = client_session.Session()
        adpt = adapter.Adapter(sess, auth=auth)

        adpt.invalidate()

        self.assertTrue(auth.invalidate_called)

    def test_adapter_get_token(self):
        auth = CalledAuthPlugin()
        sess = client_session.Session()
        adpt = adapter.Adapter(sess, auth=auth)

        self.assertEqual(self.TEST_TOKEN, adpt.get_token())
        self.assertTrue(auth.get_token_called)

    def test_adapter_connect_retries(self):
        retries = 2
        sess = client_session.Session()
        adpt = adapter.Adapter(sess, connect_retries=retries)

        self.stub_url('GET', exc=requests.exceptions.ConnectionError())

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.ConnectionError,
                              adpt.get, self.TEST_URL)
            self.assertEqual(retries, m.call_count)

        # we count retries so there will be one initial request + 2 retries
        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(retries + 1))

    def test_adapter_http_503_retries(self):
        retries = 2
        sess = client_session.Session()
        adpt = adapter.Adapter(sess, status_code_retries=retries)

        self.stub_url('GET', status_code=503)

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.ServiceUnavailable,
                              adpt.get, self.TEST_URL)
            self.assertEqual(retries, m.call_count)

        # we count retries so there will be one initial request + 2 retries
        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(retries + 1))

    def test_adapter_http_status_retries(self):
        retries = 2
        sess = client_session.Session()
        adpt = adapter.Adapter(sess, status_code_retries=retries,
                               retriable_status_codes=[503, 409])

        self.stub_url('GET', status_code=409)

        with mock.patch('time.sleep') as m:
            self.assertRaises(exceptions.Conflict,
                              adpt.get, self.TEST_URL)
            self.assertEqual(retries, m.call_count)

        # we count retries so there will be one initial request + 2 retries
        self.assertThat(self.requests_mock.request_history,
                        matchers.HasLength(retries + 1))

    def test_user_and_project_id(self):
        auth = AuthPlugin()
        sess = client_session.Session()
        adpt = adapter.Adapter(sess, auth=auth)

        self.assertEqual(auth.TEST_USER_ID, adpt.get_user_id())
        self.assertEqual(auth.TEST_PROJECT_ID, adpt.get_project_id())

    def test_logger_object_passed(self):
        logger = logging.getLogger(uuid.uuid4().hex)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        io = six.StringIO()
        handler = logging.StreamHandler(io)
        logger.addHandler(handler)

        auth = AuthPlugin()
        sess = client_session.Session(auth=auth)
        adpt = adapter.Adapter(sess, auth=auth, logger=logger)

        response = {uuid.uuid4().hex: uuid.uuid4().hex}

        self.stub_url('GET', json=response,
                      headers={'Content-Type': 'application/json'})

        resp = adpt.get(self.TEST_URL, logger=logger)

        self.assertEqual(response, resp.json())
        output = io.getvalue()

        self.assertIn(self.TEST_URL, output)
        self.assertIn(list(response.keys())[0], output)
        self.assertIn(list(response.values())[0], output)

        self.assertNotIn(list(response.keys())[0], self.logger.output)
        self.assertNotIn(list(response.values())[0], self.logger.output)

    def test_unknown_connection_error(self):
        self.stub_url('GET', exc=requests.exceptions.RequestException)
        self.assertRaises(exceptions.UnknownConnectionError,
                          client_session.Session().request,
                          self.TEST_URL,
                          'GET')

    def test_additional_headers(self):
        session_key = uuid.uuid4().hex
        session_val = uuid.uuid4().hex
        adapter_key = uuid.uuid4().hex
        adapter_val = uuid.uuid4().hex
        request_key = uuid.uuid4().hex
        request_val = uuid.uuid4().hex
        text = uuid.uuid4().hex

        url = 'http://keystone.test.com'
        self.requests_mock.get(url, text=text)

        sess = client_session.Session(
            additional_headers={session_key: session_val})
        adap = adapter.Adapter(session=sess,
                               additional_headers={adapter_key: adapter_val})
        resp = adap.get(url, headers={request_key: request_val})

        request = self.requests_mock.last_request

        self.assertEqual(resp.text, text)
        self.assertEqual(session_val, request.headers[session_key])
        self.assertEqual(adapter_val, request.headers[adapter_key])
        self.assertEqual(request_val, request.headers[request_key])

    def test_additional_headers_overrides(self):
        header = uuid.uuid4().hex
        session_val = uuid.uuid4().hex
        adapter_val = uuid.uuid4().hex
        request_val = uuid.uuid4().hex

        url = 'http://keystone.test.com'
        self.requests_mock.get(url)

        sess = client_session.Session(additional_headers={header: session_val})
        adap = adapter.Adapter(session=sess)

        adap.get(url)
        self.assertEqual(session_val,
                         self.requests_mock.last_request.headers[header])

        adap.additional_headers[header] = adapter_val
        adap.get(url)
        self.assertEqual(adapter_val,
                         self.requests_mock.last_request.headers[header])

        adap.get(url, headers={header: request_val})
        self.assertEqual(request_val,
                         self.requests_mock.last_request.headers[header])

    def test_adapter_user_agent_session_adapter(self):
        sess = client_session.Session(app_name='ksatest', app_version='1.2.3')
        adap = adapter.Adapter(client_name='testclient',
                               client_version='4.5.6',
                               session=sess)

        url = 'http://keystone.test.com'
        self.requests_mock.get(url)

        adap.get(url)

        agent = 'ksatest/1.2.3 testclient/4.5.6'
        self.assertEqual(agent + ' ' + client_session.DEFAULT_USER_AGENT,
                         self.requests_mock.last_request.headers['User-Agent'])

    def test_adapter_user_agent_session_version_on_adapter(self):

        class TestAdapter(adapter.Adapter):

            client_name = 'testclient'
            client_version = '4.5.6'

        sess = client_session.Session(app_name='ksatest', app_version='1.2.3')
        adap = TestAdapter(session=sess)

        url = 'http://keystone.test.com'
        self.requests_mock.get(url)

        adap.get(url)

        agent = 'ksatest/1.2.3 testclient/4.5.6'
        self.assertEqual(agent + ' ' + client_session.DEFAULT_USER_AGENT,
                         self.requests_mock.last_request.headers['User-Agent'])

    def test_adapter_user_agent_session_adapter_no_app_version(self):
        sess = client_session.Session(app_name='ksatest')
        adap = adapter.Adapter(client_name='testclient',
                               client_version='4.5.6',
                               session=sess)

        url = 'http://keystone.test.com'
        self.requests_mock.get(url)

        adap.get(url)

        agent = 'ksatest testclient/4.5.6'
        self.assertEqual(agent + ' ' + client_session.DEFAULT_USER_AGENT,
                         self.requests_mock.last_request.headers['User-Agent'])

    def test_adapter_user_agent_session_adapter_no_client_version(self):
        sess = client_session.Session(app_name='ksatest', app_version='1.2.3')
        adap = adapter.Adapter(client_name='testclient', session=sess)

        url = 'http://keystone.test.com'
        self.requests_mock.get(url)

        adap.get(url)

        agent = 'ksatest/1.2.3 testclient'
        self.assertEqual(agent + ' ' + client_session.DEFAULT_USER_AGENT,
                         self.requests_mock.last_request.headers['User-Agent'])

    def test_adapter_user_agent_session_adapter_additional(self):
        sess = client_session.Session(app_name='ksatest',
                                      app_version='1.2.3',
                                      additional_user_agent=[('one', '1.1.1'),
                                                             ('two', '2.2.2')])
        adap = adapter.Adapter(client_name='testclient',
                               client_version='4.5.6',
                               session=sess)

        url = 'http://keystone.test.com'
        self.requests_mock.get(url)

        adap.get(url)

        agent = 'ksatest/1.2.3 testclient/4.5.6 one/1.1.1 two/2.2.2'
        self.assertEqual(agent + ' ' + client_session.DEFAULT_USER_AGENT,
                         self.requests_mock.last_request.headers['User-Agent'])

    def test_adapter_user_agent_session(self):
        sess = client_session.Session(app_name='ksatest', app_version='1.2.3')
        adap = adapter.Adapter(session=sess)

        url = 'http://keystone.test.com'
        self.requests_mock.get(url)

        adap.get(url)

        agent = 'ksatest/1.2.3'
        self.assertEqual(agent + ' ' + client_session.DEFAULT_USER_AGENT,
                         self.requests_mock.last_request.headers['User-Agent'])

    def test_adapter_user_agent_adapter(self):
        sess = client_session.Session()
        adap = adapter.Adapter(client_name='testclient',
                               client_version='4.5.6',
                               session=sess)

        url = 'http://keystone.test.com'
        self.requests_mock.get(url)

        adap.get(url)

        agent = 'testclient/4.5.6'
        self.assertEqual(agent + ' ' + client_session.DEFAULT_USER_AGENT,
                         self.requests_mock.last_request.headers['User-Agent'])

    def test_adapter_user_agent_session_override(self):
        sess = client_session.Session(app_name='ksatest',
                                      app_version='1.2.3',
                                      additional_user_agent=[('one', '1.1.1'),
                                                             ('two', '2.2.2')])
        adap = adapter.Adapter(client_name='testclient',
                               client_version='4.5.6',
                               session=sess)

        url = 'http://keystone.test.com'
        self.requests_mock.get(url)

        override_user_agent = '%s/%s' % (uuid.uuid4().hex, uuid.uuid4().hex)
        adap.get(url, user_agent=override_user_agent)

        self.assertEqual(override_user_agent,
                         self.requests_mock.last_request.headers['User-Agent'])

    def test_nested_adapters(self):
        text = uuid.uuid4().hex
        token = uuid.uuid4().hex
        url = 'http://keystone.example.com/path'

        sess = client_session.Session()
        auth = CalledAuthPlugin()
        auth.ENDPOINT = url
        auth.TOKEN = token

        adap1 = adapter.Adapter(session=sess,
                                interface='public')
        adap2 = adapter.Adapter(session=adap1,
                                service_type='identity',
                                auth=auth)

        self.requests_mock.get(url + '/test', text=text)

        resp = adap2.get('/test')

        self.assertEqual(text, resp.text)
        self.assertTrue(auth.get_endpoint_called)

        self.assertEqual('public', auth.endpoint_arguments['interface'])
        self.assertEqual('identity', auth.endpoint_arguments['service_type'])

        last_token = self.requests_mock.last_request.headers['X-Auth-Token']
        self.assertEqual(token, last_token)

    def test_default_microversion(self):
        sess = client_session.Session()
        url = 'http://url'

        def validate(adap_kwargs, get_kwargs, exp_kwargs):
            with mock.patch.object(sess, 'request') as m:
                adapter.Adapter(sess, **adap_kwargs).get(url, **get_kwargs)
                m.assert_called_once_with(url, 'GET', endpoint_filter={},
                                          headers={}, rate_semaphore=mock.ANY,
                                          **exp_kwargs)

        # No default_microversion in Adapter, no microversion in get()
        validate({}, {}, {})

        # default_microversion in Adapter, no microversion in get()
        validate({'default_microversion': '1.2'}, {}, {'microversion': '1.2'})

        # No default_microversion in Adapter, microversion specified in get()
        validate({}, {'microversion': '1.2'}, {'microversion': '1.2'})

        # microversion in get() overrides default_microversion in Adapter
        validate({'default_microversion': '1.2'}, {'microversion': '1.5'},
                 {'microversion': '1.5'})

    def test_raise_exc_override(self):
        sess = client_session.Session()
        url = 'http://url'

        def validate(adap_kwargs, get_kwargs, exp_kwargs):
            with mock.patch.object(sess, 'request') as m:
                adapter.Adapter(sess, **adap_kwargs).get(url, **get_kwargs)
                m.assert_called_once_with(url, 'GET', endpoint_filter={},
                                          headers={}, rate_semaphore=mock.ANY,
                                          **exp_kwargs)

        # No raise_exc in Adapter or get()
        validate({}, {}, {})

        # Set in Adapter, unset in get()
        validate({'raise_exc': True}, {}, {'raise_exc': True})
        validate({'raise_exc': False}, {}, {'raise_exc': False})

        # Unset in Adapter, set in get()
        validate({}, {'raise_exc': True}, {'raise_exc': True})
        validate({}, {'raise_exc': False}, {'raise_exc': False})

        # Setting in get() overrides the one in Adapter
        validate({'raise_exc': True}, {'raise_exc': False},
                 {'raise_exc': False})
        validate({'raise_exc': False}, {'raise_exc': True},
                 {'raise_exc': True})


class TCPKeepAliveAdapterTest(utils.TestCase):

    def setUp(self):
        super(TCPKeepAliveAdapterTest, self).setUp()
        self.init_poolmanager = self.patch(
            client_session.requests.adapters.HTTPAdapter,
            'init_poolmanager')
        self.constructor = self.patch(
            client_session.TCPKeepAliveAdapter, '__init__', lambda self: None)

    def test_init_poolmanager_with_requests_lesser_than_2_4_1(self):
        self.patch(client_session, 'REQUESTS_VERSION', (2, 4, 0))
        given_adapter = client_session.TCPKeepAliveAdapter()

        # when pool manager is initialized
        given_adapter.init_poolmanager(1, 2, 3)

        # then no socket_options are given
        self.init_poolmanager.assert_called_once_with(1, 2, 3)

    def test_init_poolmanager_with_basic_options(self):
        self.patch(client_session, 'REQUESTS_VERSION', (2, 4, 1))
        socket = self.patch_socket_with_options(
            ['IPPROTO_TCP', 'TCP_NODELAY', 'SOL_SOCKET', 'SO_KEEPALIVE'])
        given_adapter = client_session.TCPKeepAliveAdapter()

        # when pool manager is initialized
        given_adapter.init_poolmanager(1, 2, 3)

        # then no socket_options are given
        self.init_poolmanager.assert_called_once_with(
            1, 2, 3, socket_options=[
                (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)])

    def test_init_poolmanager_with_tcp_keepidle(self):
        self.patch(client_session, 'REQUESTS_VERSION', (2, 4, 1))
        socket = self.patch_socket_with_options(
            ['IPPROTO_TCP', 'TCP_NODELAY', 'SOL_SOCKET', 'SO_KEEPALIVE',
             'TCP_KEEPIDLE'])
        given_adapter = client_session.TCPKeepAliveAdapter()

        # when pool manager is initialized
        given_adapter.init_poolmanager(1, 2, 3)

        # then socket_options are given
        self.init_poolmanager.assert_called_once_with(
            1, 2, 3, socket_options=[
                (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)])

    def test_init_poolmanager_with_tcp_keepcnt(self):
        self.patch(client_session, 'REQUESTS_VERSION', (2, 4, 1))
        self.patch(client_session.utils, 'is_windows_linux_subsystem', False)
        socket = self.patch_socket_with_options(
            ['IPPROTO_TCP', 'TCP_NODELAY', 'SOL_SOCKET', 'SO_KEEPALIVE',
             'TCP_KEEPCNT'])
        given_adapter = client_session.TCPKeepAliveAdapter()

        # when pool manager is initialized
        given_adapter.init_poolmanager(1, 2, 3)

        # then socket_options are given
        self.init_poolmanager.assert_called_once_with(
            1, 2, 3, socket_options=[
                (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 4)])

    def test_init_poolmanager_with_tcp_keepcnt_on_windows(self):
        self.patch(client_session, 'REQUESTS_VERSION', (2, 4, 1))
        self.patch(client_session.utils, 'is_windows_linux_subsystem', True)
        socket = self.patch_socket_with_options(
            ['IPPROTO_TCP', 'TCP_NODELAY', 'SOL_SOCKET', 'SO_KEEPALIVE',
             'TCP_KEEPCNT'])
        given_adapter = client_session.TCPKeepAliveAdapter()

        # when pool manager is initialized
        given_adapter.init_poolmanager(1, 2, 3)

        # then socket_options are given
        self.init_poolmanager.assert_called_once_with(
            1, 2, 3, socket_options=[
                (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)])

    def test_init_poolmanager_with_tcp_keepintvl(self):
        self.patch(client_session, 'REQUESTS_VERSION', (2, 4, 1))
        socket = self.patch_socket_with_options(
            ['IPPROTO_TCP', 'TCP_NODELAY', 'SOL_SOCKET', 'SO_KEEPALIVE',
             'TCP_KEEPINTVL'])
        given_adapter = client_session.TCPKeepAliveAdapter()

        # when pool manager is initialized
        given_adapter.init_poolmanager(1, 2, 3)

        # then socket_options are given
        self.init_poolmanager.assert_called_once_with(
            1, 2, 3, socket_options=[
                (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 15)])

    def test_init_poolmanager_with_given_optionsl(self):
        self.patch(client_session, 'REQUESTS_VERSION', (2, 4, 1))
        given_adapter = client_session.TCPKeepAliveAdapter()
        given_options = object()

        # when pool manager is initialized
        given_adapter.init_poolmanager(1, 2, 3, socket_options=given_options)

        # then socket_options are given
        self.init_poolmanager.assert_called_once_with(
            1, 2, 3, socket_options=given_options)

    def patch_socket_with_options(self, option_names):
        # to mock socket module with exactly the attributes I want I create
        # a class with that attributes
        socket = type('socket', (object,),
                      {name: 'socket.' + name for name in option_names})
        return self.patch(client_session, 'socket', socket)

    def patch(self, target, name, *args, **kwargs):
        context = mock.patch.object(target, name, *args, **kwargs)
        patch = context.start()
        self.addCleanup(context.stop)
        return patch
