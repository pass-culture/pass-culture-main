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
import functools
import hashlib
import json
import logging
import os
import platform
import socket
import sys
import time
import uuid

import requests
import six
from six.moves import urllib

import keystoneauth1
from keystoneauth1 import _utils as utils
from keystoneauth1 import discover
from keystoneauth1 import exceptions

try:
    import netaddr
except ImportError:
    netaddr = None

try:
    import osprofiler.web as osprofiler_web
except ImportError:
    osprofiler_web = None

DEFAULT_USER_AGENT = 'keystoneauth1/%s %s %s/%s' % (
    keystoneauth1.__version__, requests.utils.default_user_agent(),
    platform.python_implementation(), platform.python_version())

# NOTE(jamielennox): Clients will likely want to print more than json. Please
# propose a patch if you have a content type you think is reasonable to print
# here and we'll add it to the list as required.
_LOG_CONTENT_TYPES = set(['application/json'])

_MAX_RETRY_INTERVAL = 60.0
_EXPONENTIAL_DELAY_START = 0.5

# NOTE(efried): This is defined in oslo_middleware.request_id.INBOUND_HEADER,
# but it didn't seem worth adding oslo_middleware to requirements just for that
_REQUEST_ID_HEADER = 'X-Openstack-Request-Id'


def _construct_session(session_obj=None):
    # NOTE(morganfainberg): if the logic in this function changes be sure to
    # update the betamax fixture's '_construct_session_with_betamax" function
    # as well.
    if not session_obj:
        session_obj = requests.Session()
        # Use TCPKeepAliveAdapter to fix bug 1323862
        for scheme in list(session_obj.adapters):
            session_obj.mount(scheme, TCPKeepAliveAdapter())
    return session_obj


def _mv_legacy_headers_for_service(mv_service_type):
    """Workaround for services that predate standardization.

    TODO(sdague): eventually convert this to using os-service-types
    and put the logic there. However, right now this is so little
    logic, inlining it for release is a better call.

    """
    headers = []
    if mv_service_type == "compute":
        headers.append("X-OpenStack-Nova-API-Version")
    elif mv_service_type == "baremetal":
        headers.append("X-OpenStack-Ironic-API-Version")
    return headers


def _sanitize_headers(headers):
    """Ensure headers are strings and not bytes."""
    str_dict = {}
    for k, v in headers.items():
        if six.PY3:
            # requests expects headers to be str type in python3, which means
            # if we get a bytes we need to decode it into a str
            k = k.decode('ASCII') if isinstance(k, six.binary_type) else k
            if v is not None:
                v = v.decode('ASCII') if isinstance(v, six.binary_type) else v
        else:
            # requests expects headers to be str type in python2, which means
            # if we get a unicode we need to encode it to ASCII into a str
            k = k.encode('ASCII') if isinstance(k, six.text_type) else k
            if v is not None:
                v = v.encode('ASCII') if isinstance(v, six.text_type) else v
        str_dict[k] = v
    return str_dict


class NoOpSemaphore(object):
    """Empty context manager for use as a default semaphore."""

    def __enter__(self):
        """Enter the context manager and do nothing."""
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager and do nothing."""
        pass


class _JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, uuid.UUID):
            return six.text_type(o)
        if netaddr and isinstance(o, netaddr.IPAddress):
            return six.text_type(o)

        return super(_JSONEncoder, self).default(o)


class _StringFormatter(object):
    """A String formatter that fetches values on demand."""

    def __init__(self, session, auth):
        self.session = session
        self.auth = auth

    def __getitem__(self, item):
        if item == 'project_id':
            value = self.session.get_project_id(self.auth)
        elif item == 'user_id':
            value = self.session.get_user_id(self.auth)
        else:
            raise AttributeError(item)

        if not value:
            raise ValueError("This type of authentication does not provide a "
                             "%s that can be substituted" % item)

        return value


def _determine_calling_package():
    """Walk the call frames trying to identify what is using this module."""
    # Create a lookup table mapping file name to module name. The ``inspect``
    # module does this but is far less efficient. Same story with the
    # frame walking below.  One could use ``inspect.stack()`` but it
    # has far more overhead.
    mod_lookup = dict((m.__file__, n) for n, m in sys.modules.items()
                      if hasattr(m, '__file__'))

    # NOTE(shaleh): these are not useful because they hide the real
    # user of the code. debtcollector did not import keystoneauth but
    # it will show up in the call stack. Similarly we do not want to
    # report ourselves or keystone client as the user agent. The real
    # user is the code importing them.
    ignored = ('debtcollector', 'keystoneauth1', 'keystoneclient')

    i = 0
    while True:
        i += 1

        try:
            # NOTE(shaleh): this is safe in CPython but could break in
            # other implementations of Python. Yes, the `inspect`
            # module could be used instead. But it does a lot more
            # work so it has worse performance.
            f = sys._getframe(i)
            try:
                name = mod_lookup[f.f_code.co_filename]
                # finds the full name module.foo.bar but all we need
                # is the module name.
                name, _, _ = name.partition('.')
                if name not in ignored:
                    return name
            except KeyError:
                pass  # builtin or the like
        except ValueError:
            # hit the bottom of the frame stack
            break

    return ''


def _determine_user_agent():
    """Attempt to programmatically generate a user agent string.

    First, look at the name of the process. Return this unless it is in
    the `ignored` list.  Otherwise, look at the function call stack and
    try to find the name of the code that invoked this module.
    """
    # NOTE(shaleh): mod_wsgi is not any more useful than just
    # reporting "keystoneauth". Ignore it and perform the package name
    # heuristic.
    ignored = ('mod_wsgi', )

    try:
        name = sys.argv[0]
    except IndexError:
        # sys.argv is empty, usually the Python interpreter prevents this.
        return ''

    if not name:
        return ''

    name = os.path.basename(name)
    if name in ignored:
        name = _determine_calling_package()
    return name


class RequestTiming(object):
    """Contains timing information for an HTTP interaction."""

    #: HTTP method used for the call (GET, POST, etc)
    method = None

    #: URL against which the call was made
    url = None

    #: Elapsed time information
    elapsed = None  # type: datetime.timedelta

    def __init__(self, method, url, elapsed):
        self.method = method
        self.url = url
        self.elapsed = elapsed


class _Retries(object):
    __slots__ = ('_fixed_delay', '_current')

    def __init__(self, fixed_delay=None):
        self._fixed_delay = fixed_delay
        self.reset()

    def __next__(self):
        value = self._current
        if not self._fixed_delay:
            self._current = min(value * 2, _MAX_RETRY_INTERVAL)
        return value

    def reset(self):
        if self._fixed_delay:
            self._current = self._fixed_delay
        else:
            self._current = _EXPONENTIAL_DELAY_START

    # Python 2 compatibility
    next = __next__


class Session(object):
    """Maintains client communication state and common functionality.

    As much as possible the parameters to this class reflect and are passed
    directly to the :mod:`requests` library.

    :param auth: An authentication plugin to authenticate the session with.
                 (optional, defaults to None)
    :type auth: keystoneauth1.plugin.BaseAuthPlugin
    :param requests.Session session: A requests session object that can be used
                                     for issuing requests. (optional)
    :param str original_ip: The original IP of the requesting user which will
                            be sent to identity service in a 'Forwarded'
                            header. (optional)
    :param verify: The verification arguments to pass to requests. These are of
                   the same form as requests expects, so True or False to
                   verify (or not) against system certificates or a path to a
                   bundle or CA certs to check against or None for requests to
                   attempt to locate and use certificates. (optional, defaults
                   to True)
    :param cert: A client certificate to pass to requests. These are of the
                 same form as requests expects. Either a single filename
                 containing both the certificate and key or a tuple containing
                 the path to the certificate then a path to the key. (optional)
    :param float timeout: A timeout to pass to requests. This should be a
                          numerical value indicating some amount (or fraction)
                          of seconds or 0 for no timeout. (optional, defaults
                          to 0)
    :param str user_agent: A User-Agent header string to use for the request.
                           If not provided, a default of
                           :attr:`~keystoneauth1.session.DEFAULT_USER_AGENT` is
                           used, which contains the keystoneauth1 version as
                           well as those of the requests library and which
                           Python is being used. When a non-None value is
                           passed, it will be prepended to the default.
    :param int/bool redirect: Controls the maximum number of redirections that
                              can be followed by a request. Either an integer
                              for a specific count or True/False for
                              forever/never. (optional, default to 30)
    :param dict additional_headers: Additional headers that should be attached
                                    to every request passing through the
                                    session. Headers of the same name specified
                                    per request will take priority.
    :param str app_name: The name of the application that is creating the
                         session. This will be used to create the user_agent.
    :param str app_version: The version of the application creating the
                            session. This will be used to create the
                            user_agent.
    :param list additional_user_agent: A list of tuple of name, version that
                                       will be added to the user agent. This
                                       can be used by libraries that are part
                                       of the communication process.
    :param dict discovery_cache: A dict to be used for caching of discovery
                                 information. This is normally managed
                                 transparently, but if the user wants to
                                 share a single cache across multiple sessions
                                 that do not share an auth plugin, it can
                                 be provided here. (optional, defaults to
                                 None which means automatically manage)
    :param bool split_loggers: Split the logging of requests across multiple
                               loggers instead of just one. Defaults to False.
    :param bool collect_timing: Whether or not to collect per-method timing
                                information for each API call. (optional,
                                defaults to False)
    :param rate_semaphore: Semaphore to be used to control concurrency
                           and rate limiting of requests. (optional,
                           defaults to no concurrency or rate control)
    :param int connect_retries: the maximum number of retries that should
                                be attempted for connection errors.
                                (optional, defaults to 0 - never retry).
    """

    user_agent = None

    _REDIRECT_STATUSES = (301, 302, 303, 305, 307, 308)

    _DEFAULT_REDIRECT_LIMIT = 30

    def __init__(self, auth=None, session=None, original_ip=None, verify=True,
                 cert=None, timeout=None, user_agent=None,
                 redirect=_DEFAULT_REDIRECT_LIMIT, additional_headers=None,
                 app_name=None, app_version=None, additional_user_agent=None,
                 discovery_cache=None, split_loggers=None,
                 collect_timing=False, rate_semaphore=None,
                 connect_retries=0):

        self.auth = auth
        self.session = _construct_session(session)
        # NOTE(mwhahaha): keep a reference to the session object so we can
        # clean it up when this object goes away. We don't want to close the
        # session if it was passed into us as it may be reused externally.
        # See LP#1838704
        self._session = None
        if not session:
            self._session = self.session
        self.original_ip = original_ip
        self.verify = verify
        self.cert = cert
        self.timeout = None
        self.redirect = redirect
        self.additional_headers = additional_headers or {}
        self.app_name = app_name
        self.app_version = app_version
        self.additional_user_agent = additional_user_agent or []
        self._determined_user_agent = None
        if discovery_cache is None:
            discovery_cache = {}
        self._discovery_cache = discovery_cache
        # NOTE(mordred) split_loggers kwarg default is None rather than False
        # so we can distinguish between the value being set or not.
        self._split_loggers = split_loggers
        self._collect_timing = collect_timing
        self._connect_retries = connect_retries
        self._api_times = []
        self._rate_semaphore = rate_semaphore or NoOpSemaphore()

        if timeout is not None:
            self.timeout = float(timeout)

        if user_agent is not None:
            self.user_agent = "%s %s" % (user_agent, DEFAULT_USER_AGENT)

        self._json = _JSONEncoder()

    def __del__(self):
        """Clean up resources on delete."""
        if self._session:
            # If we created a requests.Session, try to close it out correctly
            try:
                self._session.close()
            except Exception:
                pass
            finally:
                self._session = None

    @property
    def adapters(self):
        return self.session.adapters

    @adapters.setter
    def adapters(self, value):
        self.session.adapters = value

    def mount(self, scheme, adapter):
        self.session.mount(scheme, adapter)

    def _remove_service_catalog(self, body):
        try:
            data = json.loads(body)

            # V3 token
            if 'token' in data and 'catalog' in data['token']:
                data['token']['catalog'] = '<removed>'
                return self._json.encode(data)

            # V2 token
            if 'serviceCatalog' in data['access']:
                data['access']['serviceCatalog'] = '<removed>'
                return self._json.encode(data)

        except Exception:
            # Don't fail trying to clean up the request body.
            pass
        return body

    @staticmethod
    def _process_header(header):
        """Redact the secure headers to be logged."""
        secure_headers = ('authorization', 'x-auth-token',
                          'x-subject-token', 'x-service-token')
        if header[0].lower() in secure_headers:
            token_hasher = hashlib.sha256()
            token_hasher.update(header[1].encode('utf-8'))
            token_hash = token_hasher.hexdigest()
            return (header[0], '{SHA256}%s' % token_hash)
        return header

    def _get_split_loggers(self, split_loggers):
        """Get a boolean value from the various argument sources.

        We default split_loggers to None in the kwargs of the Session
        constructor so we can track set vs. not set. We also accept
        split_loggers as a parameter in a few other places. In each place
        we want the parameter, if given by the user, to win.
        """
        # None is the default value in each method's kwarg. None means "unset".
        if split_loggers is None:
            # If no value was given, try the value set on the instance.
            split_loggers = self._split_loggers
        if split_loggers is None:
            # If neither a value was given on the method, nor a value was given
            # on the Session constructor, then the value is False.
            split_loggers = False
        return split_loggers

    def _http_log_request(self, url, method=None, data=None,
                          json=None, headers=None, query_params=None,
                          logger=None, split_loggers=None):
        string_parts = []

        if self._get_split_loggers(split_loggers):
            logger = utils.get_logger(__name__ + '.request')
        else:
            # Only a single logger was passed in, use string prefixing.
            string_parts.append('REQ:')
            if not logger:
                logger = utils.get_logger(__name__)

        if not logger.isEnabledFor(logging.DEBUG):
            # NOTE(morganfainberg): This whole debug section is expensive,
            # there is no need to do the work if we're not going to emit a
            # debug log.
            return

        string_parts.append('curl -g -i')

        # NOTE(jamielennox): None means let requests do its default validation
        # so we need to actually check that this is False.
        if self.verify is False:
            string_parts.append('--insecure')
        elif isinstance(self.verify, six.string_types):
            string_parts.append('--cacert "%s"' % self.verify)

        if method:
            string_parts.extend(['-X', method])

        if query_params:
            # Don't check against `is not None` as this can be
            # an empty dictionary, which we shouldn't bother logging.
            url = url + '?' + urllib.parse.urlencode(query_params)
            # URLs with query strings need to be wrapped in quotes in order
            # for the CURL command to run properly.
            string_parts.append('"%s"' % url)
        else:
            string_parts.append(url)

        if headers:
            # Sort headers so that testing can work consistently.
            for header in sorted(headers.items()):
                string_parts.append('-H "%s: %s"'
                                    % self._process_header(header))
        if json:
            data = self._json.encode(json)
        if data:
            if isinstance(data, six.binary_type):
                try:
                    data = data.decode("ascii")
                except UnicodeDecodeError:
                    data = "<binary_data>"
            string_parts.append("-d '%s'" % data)

        logger.debug(' '.join(string_parts))

    def _http_log_response(self, response=None, json=None,
                           status_code=None, headers=None, text=None,
                           logger=None, split_loggers=True):
        string_parts = []
        body_parts = []
        if self._get_split_loggers(split_loggers):
            logger = utils.get_logger(__name__ + '.response')
            body_logger = utils.get_logger(__name__ + '.body')
        else:
            # Only a single logger was passed in, use string prefixing.
            string_parts.append('RESP:')
            body_parts.append('RESP BODY:')
            body_logger = logger

        if not logger.isEnabledFor(logging.DEBUG):
            return

        if response is not None:
            if not status_code:
                status_code = response.status_code
            if not headers:
                headers = response.headers

        if status_code:
            string_parts.append('[%s]' % status_code)
        if headers:
            # Sort headers so that testing can work consistently.
            for header in sorted(headers.items()):
                string_parts.append('%s: %s' % self._process_header(header))
        logger.debug(' '.join(string_parts))

        if not body_logger.isEnabledFor(logging.DEBUG):
            return

        if response is not None:
            if not text:
                # NOTE(samueldmq): If the response does not provide enough info
                # about the content type to decide whether it is useful and
                # safe to log it or not, just do not log the body. Trying to
                # read the response body anyways may result on reading a long
                # stream of bytes and getting an unexpected MemoryError. See
                # bug 1616105 for further details.
                content_type = response.headers.get('content-type', None)

                # NOTE(lamt): Per [1], the Content-Type header can be of the
                # form Content-Type := type "/" subtype *[";" parameter]
                # [1] https://www.w3.org/Protocols/rfc1341/4_Content-Type.html
                for log_type in _LOG_CONTENT_TYPES:
                    if content_type is not None and content_type.startswith(
                            log_type):
                        text = self._remove_service_catalog(response.text)
                        break
                else:
                    text = ('Omitted, Content-Type is set to %s. Only '
                            '%s responses have their bodies logged.')
                    text = text % (content_type, ', '.join(_LOG_CONTENT_TYPES))
        if json:
            text = self._json.encode(json)

        if text:
            body_parts.append(text)
            body_logger.debug(' '.join(body_parts))

    @staticmethod
    def _set_microversion_headers(
            headers, microversion, service_type, endpoint_filter):
        # We're converting it to normalized version number for two reasons.
        # First, to validate it's a real version number. Second, so that in
        # the future we can pre-validate that it is within the range of
        # available microversions before we send the request.
        # TODO(mordred) Validate when we get the response back that
        # the server executed in the microversion we expected.
        # TODO(mordred) Validate that the requested microversion works
        # with the microversion range we found in discovery.
        microversion = discover.normalize_version_number(microversion)
        # Can't specify a M.latest microversion
        if (microversion[0] != discover.LATEST and
                discover.LATEST in microversion[1:]):
            raise TypeError(
                "Specifying a '{major}.latest' microversion is not allowed.")
        microversion = discover.version_to_string(microversion)
        if not service_type:
            if endpoint_filter and 'service_type' in endpoint_filter:
                service_type = endpoint_filter['service_type']
            else:
                raise TypeError(
                    "microversion {microversion} was requested but no"
                    " service_type information is available. Either provide a"
                    " service_type in endpoint_filter or pass"
                    " microversion_service_type as an argument.".format(
                        microversion=microversion))

        # TODO(mordred) cinder uses volume in its microversion header. This
        # logic should be handled in the future by os-service-types but for
        # now hard-code for cinder.
        if (service_type.startswith('volume') or
                service_type == 'block-storage'):
            service_type = 'volume'
        headers.setdefault('OpenStack-API-Version',
                           '{service_type} {microversion}'.format(
                               service_type=service_type,
                               microversion=microversion))
        header_names = _mv_legacy_headers_for_service(service_type)
        for h in header_names:
            headers.setdefault(h, microversion)

    def request(self, url, method, json=None, original_ip=None,
                user_agent=None, redirect=None, authenticated=None,
                endpoint_filter=None, auth=None, requests_auth=None,
                raise_exc=True, allow_reauth=True, log=True,
                endpoint_override=None, connect_retries=None, logger=None,
                allow=None, client_name=None, client_version=None,
                microversion=None, microversion_service_type=None,
                status_code_retries=0, retriable_status_codes=None,
                rate_semaphore=None, global_request_id=None,
                connect_retry_delay=None, status_code_retry_delay=None,
                **kwargs):
        """Send an HTTP request with the specified characteristics.

        Wrapper around `requests.Session.request` to handle tasks such as
        setting headers, JSON encoding/decoding, and error handling.

        Arguments that are not handled are passed through to the requests
        library.

        :param str url: Path or fully qualified URL of HTTP request. If only a
                        path is provided then endpoint_filter must also be
                        provided such that the base URL can be determined. If a
                        fully qualified URL is provided then endpoint_filter
                        will be ignored.
        :param str method: The http method to use. (e.g. 'GET', 'POST')
        :param str original_ip: Mark this request as forwarded for this ip.
                                (optional)
        :param dict headers: Headers to be included in the request. (optional)
        :param json: Some data to be represented as JSON. (optional)
        :param str user_agent: A user_agent to use for the request. If present
                               will override one present in headers. (optional)
        :param int/bool redirect: the maximum number of redirections that
                                  can be followed by a request. Either an
                                  integer for a specific count or True/False
                                  for forever/never. (optional)
        :param int connect_retries: the maximum number of retries that should
                                    be attempted for connection errors.
                                    (optional, defaults to None - never retry).
        :param bool authenticated: True if a token should be attached to this
                                   request, False if not or None for attach if
                                   an auth_plugin is available.
                                   (optional, defaults to None)
        :param dict endpoint_filter: Data to be provided to an auth plugin with
                                     which it should be able to determine an
                                     endpoint to use for this request. If not
                                     provided then URL is expected to be a
                                     fully qualified URL. (optional)
        :param str endpoint_override: The URL to use instead of looking up the
                                      endpoint in the auth plugin. This will be
                                      ignored if a fully qualified URL is
                                      provided but take priority over an
                                      endpoint_filter. This string may contain
                                      the values ``%(project_id)s`` and
                                      ``%(user_id)s`` to have those values
                                      replaced by the project_id/user_id of the
                                      current authentication. (optional)
        :param auth: The auth plugin to use when authenticating this request.
                     This will override the plugin that is attached to the
                     session (if any). (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin
        :param requests_auth: A requests library auth plugin that cannot be
                              passed via kwarg because the `auth` kwarg
                              collides with our own auth plugins. (optional)
        :type requests_auth: :py:class:`requests.auth.AuthBase`
        :param bool raise_exc: If True then raise an appropriate exception for
                               failed HTTP requests. If False then return the
                               request object. (optional, default True)
        :param bool allow_reauth: Allow fetching a new token and retrying the
                                  request on receiving a 401 Unauthorized
                                  response. (optional, default True)
        :param bool log: If True then log the request and response data to the
                         debug log. (optional, default True)
        :param logger: The logger object to use to log request and responses.
                       If not provided the keystoneauth1.session default
                       logger will be used.
        :type logger: logging.Logger
        :param dict allow: Extra filters to pass when discovering API
                           versions. (optional)
        :param microversion: Microversion to send for this request.
                       microversion can be given as a string or a tuple.
                       (optional)
        :param str microversion_service_type: The service_type to be sent in
                       the microversion header, if a microversion is given.
                       Defaults to the value of service_type from
                       endpoint_filter if one exists. If endpoint_filter is not
                       provided or does not have a service_type, microversion
                       is given and microversion_service_type is not provided,
                       an exception will be raised.
        :param int status_code_retries: the maximum number of retries that
                                        should be attempted for retriable
                                        HTTP status codes (optional, defaults
                                        to 0 - never retry).
        :param list retriable_status_codes: list of HTTP status codes that
                                            should be retried (optional,
                                            defaults to HTTP 503, has no effect
                                            when status_code_retries is 0).
        :param rate_semaphore: Semaphore to be used to control concurrency
                               and rate limiting of requests. (optional,
                               defaults to no concurrency or rate control)
        :param global_request_id: Value for the X-Openstack-Request-Id header.
        :param float connect_retry_delay: Delay (in seconds) between two
                                          connect retries (if enabled).
                                          By default exponential retry starting
                                          with 0.5 seconds up to a maximum of
                                          60 seconds is used.
        :param float status_code_retry_delay: Delay (in seconds) between two
                                              status code retries (if enabled).
                                              By default exponential retry
                                              starting with 0.5 seconds up to
                                              a maximum of 60 seconds is used.
        :param kwargs: any other parameter that can be passed to
                       :meth:`requests.Session.request` (such as `headers`).
                       Except:

                       - `data` will be overwritten by the data in the `json`
                         param.
                       - `allow_redirects` is ignored as redirects are handled
                         by the session.

        :raises keystoneauth1.exceptions.base.ClientException: For connection
            failure, or to indicate an error response code.

        :returns: The response to the request.
        """
        # If a logger is passed in, use it and do not log requests, responses
        # and bodies separately.
        if logger:
            split_loggers = False
        else:
            split_loggers = None
        logger = logger or utils.get_logger(__name__)
        # NOTE(gmann): Convert r initlize the headers to
        # CaseInsensitiveDict to make sure headers are
        # case insensitive.
        if kwargs.get('headers'):
            kwargs['headers'] = requests.structures.CaseInsensitiveDict(
                kwargs['headers'])
        else:
            kwargs['headers'] = requests.structures.CaseInsensitiveDict()
        if connect_retries is None:
            connect_retries = self._connect_retries
        # HTTP 503 - Service Unavailable
        retriable_status_codes = retriable_status_codes or [503]
        rate_semaphore = rate_semaphore or self._rate_semaphore

        headers = kwargs.setdefault('headers', dict())
        if microversion:
            self._set_microversion_headers(
                headers, microversion, microversion_service_type,
                endpoint_filter)

        if authenticated is None:
            authenticated = bool(auth or self.auth)

        if authenticated:
            auth_headers = self.get_auth_headers(auth)

            if auth_headers is None:
                msg = 'No valid authentication is available'
                raise exceptions.AuthorizationFailure(msg)

            headers.update(auth_headers)

        if osprofiler_web:
            headers.update(osprofiler_web.get_trace_id_headers())

        # if we are passed a fully qualified URL and an endpoint_filter we
        # should ignore the filter. This will make it easier for clients who
        # want to overrule the default endpoint_filter data added to all client
        # requests. We check fully qualified here by the presence of a host.
        if not urllib.parse.urlparse(url).netloc:
            base_url = None

            if endpoint_override:
                base_url = endpoint_override % _StringFormatter(self, auth)
            elif endpoint_filter:
                base_url = self.get_endpoint(auth, allow=allow,
                                             **endpoint_filter)

            if not base_url:
                raise exceptions.EndpointNotFound()

            url = '%s/%s' % (base_url.rstrip('/'), url.lstrip('/'))

        if self.cert:
            kwargs.setdefault('cert', self.cert)

        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)

        if user_agent:
            headers['User-Agent'] = user_agent
        elif self.user_agent:
            user_agent = headers.setdefault('User-Agent', self.user_agent)
        else:
            # Per RFC 7231 Section 5.5.3, identifiers in a user-agent should be
            # ordered by decreasing significance.  If a user sets their product
            # that value will be used. Otherwise we attempt to derive a useful
            # product value. The value will be prepended it to the KSA version,
            # requests version, and then the Python version.

            agent = []

            if self.app_name and self.app_version:
                agent.append('%s/%s' % (self.app_name, self.app_version))
            elif self.app_name:
                agent.append(self.app_name)

            if client_name and client_version:
                agent.append('%s/%s' % (client_name, client_version))
            elif client_name:
                agent.append(client_name)

            for additional in self.additional_user_agent:
                agent.append('%s/%s' % additional)

            if not agent:
                # NOTE(jamielennox): determine_user_agent will return an empty
                # string on failure so checking for None will ensure it is only
                # called once even on failure.
                if self._determined_user_agent is None:
                    self._determined_user_agent = _determine_user_agent()

                if self._determined_user_agent:
                    agent.append(self._determined_user_agent)

            agent.append(DEFAULT_USER_AGENT)
            user_agent = headers.setdefault('User-Agent', ' '.join(agent))

        if self.original_ip:
            headers.setdefault('Forwarded',
                               'for=%s;by=%s' % (self.original_ip, user_agent))

        if json is not None:
            headers.setdefault('Content-Type', 'application/json')
            kwargs['data'] = self._json.encode(json)

        if global_request_id is not None:
            # NOTE(efried): This does *not* setdefault. If a global_request_id
            # kwarg was explicitly specified, it should override any value
            # previously configured (e.g. in Adapter.global_request_id).
            headers[_REQUEST_ID_HEADER] = global_request_id

        for k, v in self.additional_headers.items():
            headers.setdefault(k, v)

        # Bug #1766235: some headers may be bytes
        headers = _sanitize_headers(headers)
        kwargs['headers'] = headers

        kwargs.setdefault('verify', self.verify)

        if requests_auth:
            kwargs['auth'] = requests_auth

        # Query parameters that are included in the url string will
        # be logged properly, but those sent in the `params` parameter
        # (which the requests library handles) need to be explicitly
        # picked out so they can be included in the URL that gets loggged.
        query_params = kwargs.get('params', dict())

        if log:
            self._http_log_request(url, method=method,
                                   data=kwargs.get('data'),
                                   headers=headers,
                                   query_params=query_params,
                                   logger=logger, split_loggers=split_loggers)

        # Force disable requests redirect handling. We will manage this below.
        kwargs['allow_redirects'] = False

        if redirect is None:
            redirect = self.redirect

        connect_retry_delays = _Retries(connect_retry_delay)
        status_code_retry_delays = _Retries(status_code_retry_delay)

        send = functools.partial(self._send_request,
                                 url, method, redirect, log, logger,
                                 split_loggers, connect_retries,
                                 status_code_retries, retriable_status_codes,
                                 rate_semaphore, connect_retry_delays,
                                 status_code_retry_delays)

        try:
            connection_params = self.get_auth_connection_params(auth=auth)
        except exceptions.MissingAuthPlugin:
            # NOTE(jamielennox): If we've gotten this far without an auth
            # plugin then we should be happy with allowing no additional
            # connection params. This will be the typical case for plugins
            # anyway.
            pass
        else:
            if connection_params:
                kwargs.update(connection_params)

        resp = send(**kwargs)

        # log callee and caller request-id for each api call
        if log:
            # service_name should be fetched from endpoint_filter if it is not
            # present then use service_type as service_name.
            service_name = None
            if endpoint_filter:
                service_name = endpoint_filter.get('service_name')
                if not service_name:
                    service_name = endpoint_filter.get('service_type')

            # Nova uses 'x-compute-request-id' and other services like
            # Glance, Cinder etc are using 'x-openstack-request-id' to store
            # request-id in the header
            request_id = (resp.headers.get('x-openstack-request-id') or
                          resp.headers.get('x-compute-request-id'))
            if request_id:
                if self._get_split_loggers(split_loggers):
                    id_logger = utils.get_logger(__name__ + '.request-id')
                else:
                    id_logger = logger
                if service_name:
                    id_logger.debug(
                        '%(method)s call to %(service_name)s for '
                        '%(url)s used request id '
                        '%(response_request_id)s', {
                            'method': resp.request.method,
                            'service_name': service_name,
                            'url': resp.url,
                            'response_request_id': request_id
                        })
                else:
                    id_logger.debug(
                        '%(method)s call to '
                        '%(url)s used request id '
                        '%(response_request_id)s', {
                            'method': resp.request.method,
                            'url': resp.url,
                            'response_request_id': request_id
                        })

        # handle getting a 401 Unauthorized response by invalidating the plugin
        # and then retrying the request. This is only tried once.
        if resp.status_code == 401 and authenticated and allow_reauth:
            if self.invalidate(auth):
                auth_headers = self.get_auth_headers(auth)

                if auth_headers is not None:
                    headers.update(auth_headers)
                    resp = send(**kwargs)

        if raise_exc and resp.status_code >= 400:
            logger.debug('Request returned failure status: %s',
                         resp.status_code)
            raise exceptions.from_response(resp, method, url)

        if self._collect_timing:
            for h in resp.history:
                self._api_times.append(RequestTiming(
                    method=h.request.method,
                    url=h.request.url,
                    elapsed=h.elapsed,
                ))
            self._api_times.append(RequestTiming(
                method=resp.request.method,
                url=resp.request.url,
                elapsed=resp.elapsed,
            ))

        return resp

    def _send_request(self, url, method, redirect, log, logger, split_loggers,
                      connect_retries, status_code_retries,
                      retriable_status_codes, rate_semaphore,
                      connect_retry_delays, status_code_retry_delays,
                      **kwargs):
        # NOTE(jamielennox): We handle redirection manually because the
        # requests lib follows some browser patterns where it will redirect
        # POSTs as GETs for certain statuses which is not want we want for an
        # API. See: https://en.wikipedia.org/wiki/Post/Redirect/Get

        # NOTE(jamielennox): The interaction between retries and redirects are
        # handled naively. We will attempt only a maximum number of retries and
        # redirects rather than per request limits. Otherwise the extreme case
        # could be redirects * retries requests. This will be sufficient in
        # most cases and can be fixed properly if there's ever a need.

        try:
            try:
                with rate_semaphore:
                    resp = self.session.request(method, url, **kwargs)
            except requests.exceptions.SSLError as e:
                msg = 'SSL exception connecting to %(url)s: %(error)s' % {
                    'url': url, 'error': e}
                raise exceptions.SSLError(msg)
            except requests.exceptions.Timeout:
                msg = 'Request to %s timed out' % url
                raise exceptions.ConnectTimeout(msg)
            except requests.exceptions.ConnectionError as e:
                # NOTE(sdague): urllib3/requests connection error is a
                # translation of SocketError. However, SocketError
                # happens for many different reasons, and that low
                # level message is often really important in figuring
                # out the difference between network misconfigurations
                # and firewall blocking.
                msg = 'Unable to establish connection to %s: %s' % (url, e)
                raise exceptions.ConnectFailure(msg)
            except requests.exceptions.RequestException as e:
                msg = 'Unexpected exception for %(url)s: %(error)s' % {
                    'url': url, 'error': e}
                raise exceptions.UnknownConnectionError(msg, e)

        except exceptions.RetriableConnectionFailure as e:
            if connect_retries <= 0:
                raise

            delay = next(connect_retry_delays)
            logger.info('Failure: %(e)s. Retrying in %(delay).1fs.',
                        {'e': e, 'delay': delay})
            time.sleep(delay)

            return self._send_request(
                url, method, redirect, log, logger, split_loggers,
                status_code_retries=status_code_retries,
                retriable_status_codes=retriable_status_codes,
                rate_semaphore=rate_semaphore,
                connect_retries=connect_retries - 1,
                connect_retry_delays=connect_retry_delays,
                status_code_retry_delays=status_code_retry_delays,
                **kwargs)

        if log:
            self._http_log_response(
                response=resp, logger=logger,
                split_loggers=split_loggers)

        if resp.status_code in self._REDIRECT_STATUSES:
            # be careful here in python True == 1 and False == 0
            if isinstance(redirect, bool):
                redirect_allowed = redirect
            else:
                redirect -= 1
                redirect_allowed = redirect >= 0

            if not redirect_allowed:
                return resp

            try:
                location = resp.headers['location']
            except KeyError:
                logger.warning("Failed to redirect request to %s as new "
                               "location was not provided.", resp.url)
            else:
                # NOTE(jamielennox): We don't keep increasing delays.
                # This request actually worked so we can reset the delay count.
                connect_retry_delays.reset()
                status_code_retry_delays.reset()
                new_resp = self._send_request(
                    location, method, redirect, log, logger, split_loggers,
                    rate_semaphore=rate_semaphore,
                    connect_retries=connect_retries,
                    status_code_retries=status_code_retries,
                    retriable_status_codes=retriable_status_codes,
                    connect_retry_delays=connect_retry_delays,
                    status_code_retry_delays=status_code_retry_delays,
                    **kwargs)

                if not isinstance(new_resp.history, list):
                    new_resp.history = list(new_resp.history)
                new_resp.history.insert(0, resp)
                resp = new_resp
        elif (resp.status_code in retriable_status_codes and
              status_code_retries > 0):

            delay = next(status_code_retry_delays)
            logger.info('Retriable status code %(code)s. Retrying in '
                        '%(delay).1fs.',
                        {'code': resp.status_code, 'delay': delay})
            time.sleep(delay)

            # NOTE(jamielennox): We don't keep increasing connection delays.
            # This request actually worked so we can reset the delay count.
            connect_retry_delays.reset()
            return self._send_request(
                url, method, redirect, log, logger, split_loggers,
                connect_retries=connect_retries,
                status_code_retries=status_code_retries - 1,
                retriable_status_codes=retriable_status_codes,
                rate_semaphore=rate_semaphore,
                connect_retry_delays=connect_retry_delays,
                status_code_retry_delays=status_code_retry_delays,
                **kwargs)

        return resp

    def head(self, url, **kwargs):
        """Perform a HEAD request.

        This calls :py:meth:`.request()` with ``method`` set to ``HEAD``.

        """
        return self.request(url, 'HEAD', **kwargs)

    def get(self, url, **kwargs):
        """Perform a GET request.

        This calls :py:meth:`.request()` with ``method`` set to ``GET``.

        """
        return self.request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        """Perform a POST request.

        This calls :py:meth:`.request()` with ``method`` set to ``POST``.

        """
        return self.request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        """Perform a PUT request.

        This calls :py:meth:`.request()` with ``method`` set to ``PUT``.

        """
        return self.request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        """Perform a DELETE request.

        This calls :py:meth:`.request()` with ``method`` set to ``DELETE``.

        """
        return self.request(url, 'DELETE', **kwargs)

    def patch(self, url, **kwargs):
        """Perform a PATCH request.

        This calls :py:meth:`.request()` with ``method`` set to ``PATCH``.

        """
        return self.request(url, 'PATCH', **kwargs)

    def _auth_required(self, auth, msg):
        if not auth:
            auth = self.auth

        if not auth:
            msg_fmt = 'An auth plugin is required to %s'
            raise exceptions.MissingAuthPlugin(msg_fmt % msg)

        return auth

    def get_auth_headers(self, auth=None, **kwargs):
        """Return auth headers as provided by the auth plugin.

        :param auth: The auth plugin to use for token. Overrides the plugin
                     on the session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin

        :raises keystoneauth1.exceptions.auth.AuthorizationFailure:
            if a new token fetch fails.
        :raises keystoneauth1.exceptions.auth_plugins.MissingAuthPlugin:
            if a plugin is not available.

        :returns: Authentication headers or None for failure.
        :rtype: :class:`dict`
        """
        auth = self._auth_required(auth, 'fetch a token')
        return auth.get_headers(self, **kwargs)

    def get_token(self, auth=None):
        """Return a token as provided by the auth plugin.

        :param auth: The auth plugin to use for token. Overrides the plugin
                     on the session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin

        :raises keystoneauth1.exceptions.auth.AuthorizationFailure:
             if a new token fetch fails.
        :raises keystoneauth1.exceptions.auth_plugins.MissingAuthPlugin:
            if a plugin is not available.

        .. warning::
            **DEPRECATED**: This assumes that the only header that is used to
            authenticate a message is ``X-Auth-Token``. This may not be
            correct. Use :meth:`get_auth_headers` instead.

        :returns: A valid token.
        :rtype: string
        """
        return (self.get_auth_headers(auth) or {}).get('X-Auth-Token')

    def get_endpoint(self, auth=None, **kwargs):
        """Get an endpoint as provided by the auth plugin.

        :param auth: The auth plugin to use for token. Overrides the plugin on
                     the session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin

        :raises keystoneauth1.exceptions.auth_plugins.MissingAuthPlugin:
            if a plugin is not available.

        :returns: An endpoint if available or None.
        :rtype: string
        """
        if 'endpoint_override' in kwargs:
            return kwargs['endpoint_override']

        auth = self._auth_required(auth, 'determine endpoint URL')

        return auth.get_endpoint(self, **kwargs)

    def get_endpoint_data(self, auth=None, **kwargs):
        """Get endpoint data as provided by the auth plugin.

        :param auth: The auth plugin to use for token. Overrides the plugin on
                     the session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin

        :raises keystoneauth1.exceptions.auth_plugins.MissingAuthPlugin:
            if a plugin is not available.
        :raises TypeError: If arguments are invalid

        :returns: Endpoint data if available or None.
        :rtype: keystoneauth1.discover.EndpointData
        """
        auth = self._auth_required(auth, 'determine endpoint URL')
        return auth.get_endpoint_data(self, **kwargs)

    def get_api_major_version(self, auth=None, **kwargs):
        """Get the major API version as provided by the auth plugin.

        :param auth: The auth plugin to use for token. Overrides the plugin on
                     the session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin

        :raises keystoneauth1.exceptions.auth_plugins.MissingAuthPlugin: if a
            plugin is not available.

        :return: The major version of the API of the service discovered.
        :rtype: tuple or None
        """
        auth = self._auth_required(auth, 'determine endpoint URL')
        return auth.get_api_major_version(self, **kwargs)

    def get_all_version_data(self, auth=None, interface='public',
                             region_name=None, service_type=None,
                             **kwargs):
        """Get version data for all services in the catalog.

        :param auth:
            The auth plugin to use for token. Overrides the plugin on
            the session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin
        :param interface:
            Type of endpoint to get version data for. Can be a single value
            or a list of values. A value of None indicates that all interfaces
            should be queried. (optional, defaults to public)
        :param string region_name:
            Region of endpoints to get version data for. A valueof None
            indicates that all regions should be queried. (optional, defaults
            to None)
        :param string service_type:
            Limit the version data to a single service. (optional, defaults
            to None)
        :returns: A dictionary keyed by region_name with values containing
            dictionaries keyed by interface with values being a list of
            `~keystoneauth1.discover.VersionData`.
        """
        auth = self._auth_required(auth, 'determine endpoint URL')
        return auth.get_all_version_data(
            self,
            interface=interface,
            region_name=region_name,
            service_type=service_type,
            **kwargs)

    def get_auth_connection_params(self, auth=None, **kwargs):
        """Return auth connection params as provided by the auth plugin.

        An auth plugin may specify connection parameters to the request like
        providing a client certificate for communication.

        We restrict the values that may be returned from this function to
        prevent an auth plugin overriding values unrelated to connection
        parmeters. The values that are currently accepted are:

        - `cert`: a path to a client certificate, or tuple of client
          certificate and key pair that are used with this request.
        - `verify`: a boolean value to indicate verifying SSL certificates
          against the system CAs or a path to a CA file to verify with.

        These values are passed to the requests library and further information
        on accepted values may be found there.

        :param auth: The auth plugin to use for tokens. Overrides the plugin
                     on the session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin

        :raises keystoneauth1.exceptions.auth.AuthorizationFailure:
            if a new token fetch fails.
        :raises keystoneauth1.exceptions.auth_plugins.MissingAuthPlugin:
            if a plugin is not available.
        :raises keystoneauth1.exceptions.auth_plugins.UnsupportedParameters:
            if the plugin returns a parameter that is not supported by this
            session.

        :returns: Authentication headers or None for failure.
        :rtype: :class:`dict`
        """
        auth = self._auth_required(auth, 'fetch connection params')
        params = auth.get_connection_params(self, **kwargs)

        # NOTE(jamielennox): There needs to be some consensus on what
        # parameters are allowed to be modified by the auth plugin here.
        # Ideally I think it would be only the send() parts of the request
        # flow. For now lets just allow certain elements.
        params_copy = params.copy()

        for arg in ('cert', 'verify'):
            try:
                kwargs[arg] = params_copy.pop(arg)
            except KeyError:
                pass

        if params_copy:
            raise exceptions.UnsupportedParameters(list(params_copy.keys()))

        return params

    def invalidate(self, auth=None):
        """Invalidate an authentication plugin.

        :param auth: The auth plugin to invalidate. Overrides the plugin on the
                     session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin

        """
        auth = self._auth_required(auth, 'validate')
        return auth.invalidate()

    def get_user_id(self, auth=None):
        """Return the authenticated user_id as provided by the auth plugin.

        :param auth: The auth plugin to use for token. Overrides the plugin
                     on the session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin

        :raises keystoneauth1.exceptions.auth.AuthorizationFailure:
            if a new token fetch fails.
        :raises keystoneauth1.exceptions.auth_plugins.MissingAuthPlugin:
            if a plugin is not available.

        :returns: Current user_id or None if not supported by plugin.
        :rtype: :class:`str`
        """
        auth = self._auth_required(auth, 'get user_id')
        return auth.get_user_id(self)

    def get_project_id(self, auth=None):
        """Return the authenticated project_id as provided by the auth plugin.

        :param auth: The auth plugin to use for token. Overrides the plugin
                     on the session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin

        :raises keystoneauth1.exceptions.auth.AuthorizationFailure:
            if a new token fetch fails.
        :raises keystoneauth1.exceptions.auth_plugins.MissingAuthPlugin:
            if a plugin is not available.

        :returns: Current project_id or None if not supported by plugin.
        :rtype: :class:`str`
        """
        auth = self._auth_required(auth, 'get project_id')
        return auth.get_project_id(self)

    def get_timings(self):
        """Return collected API timing information.

        :returns: List of `RequestTiming` objects.
        """
        return self._api_times

    def reset_timings(self):
        """Clear API timing information."""
        self._api_times = []


REQUESTS_VERSION = tuple(int(v) for v in requests.__version__.split('.'))


class TCPKeepAliveAdapter(requests.adapters.HTTPAdapter):
    """The custom adapter used to set TCP Keep-Alive on all connections.

    This Adapter also preserves the default behaviour of Requests which
    disables Nagle's Algorithm. See also:
    https://blogs.msdn.com/b/windowsazurestorage/archive/2010/06/25/nagle-s-algorithm-is-not-friendly-towards-small-requests.aspx
    """

    def init_poolmanager(self, *args, **kwargs):
        if 'socket_options' not in kwargs and REQUESTS_VERSION >= (2, 4, 1):
            socket_options = [
                # Keep Nagle's algorithm off
                (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
                # Turn on TCP Keep-Alive
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
            ]

            # Some operating systems (e.g., OSX) do not support setting
            # keepidle
            if hasattr(socket, 'TCP_KEEPIDLE'):
                socket_options += [
                    # Wait 60 seconds before sending keep-alive probes
                    (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
                ]

            # Windows subsystem for Linux does not support this feature
            if (hasattr(socket, 'TCP_KEEPCNT') and
                    not utils.is_windows_linux_subsystem):
                socket_options += [
                    # Set the maximum number of keep-alive probes
                    (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 4),
                ]

            if hasattr(socket, 'TCP_KEEPINTVL'):
                socket_options += [
                    # Send keep-alive probes every 15 seconds
                    (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 15),
                ]

            # After waiting 60 seconds, and then sending a probe once every 15
            # seconds 4 times, these options should ensure that a connection
            # hands for no longer than 2 minutes before a ConnectionError is
            # raised.
            kwargs['socket_options'] = socket_options
        super(TCPKeepAliveAdapter, self).init_poolmanager(*args, **kwargs)
