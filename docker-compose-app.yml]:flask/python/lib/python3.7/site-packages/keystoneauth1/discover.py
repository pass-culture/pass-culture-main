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

"""The passive components to version discovery.

The Discover object in discover.py contains functions that can create objects
on your behalf. These functions are not usable from within the keystoneauth1
library because you will get dependency resolution issues.

The Discover object in this file provides the querying components of Discovery.
This includes functions like url_for which allow you to retrieve URLs and the
raw data specified in version discovery responses.
"""

import copy
import re

import os_service_types
import six
from six.moves import urllib

from keystoneauth1 import _utils as utils
from keystoneauth1 import exceptions


_LOGGER = utils.get_logger(__name__)

LATEST = float('inf')
_SERVICE_TYPES = os_service_types.ServiceTypes()


def _str_or_latest(val):
    """Convert val to a string, handling LATEST => 'latest'.

    :param val: An int or the special value LATEST.
    :return: A string representation of val.  If val was LATEST, the return is
             'latest'.
    """
    return 'latest' if val == LATEST else str(val)


def _int_or_latest(val):
    """Convert val to an int or the special value LATEST.

    :param val: An int()-able, or the string 'latest', or the special value
                LATEST.
    :return: An int, or the special value LATEST
    """
    return LATEST if val == 'latest' or val == LATEST else int(val)


def get_version_data(session, url, authenticated=None):
    """Retrieve raw version data from a url.

    The return is a list of dicts of the form::

      [{
          'status': 'STABLE',
          'id': 'v2.3',
          'links': [
              {
                  'href': 'http://network.example.com/v2.3',
                  'rel': 'self',
              },
              {
                  'href': 'http://network.example.com/',
                  'rel': 'collection',
              },
          ],
          'min_version': '2.0',
          'max_version': '2.7',
       },
       ...,
      ]

    Note:
    The maximum microversion may be specified by `max_version` or `version`,
    the former superseding the latter.
    All `*version` keys are optional.
    Other keys and 'links' entries are permitted, but ignored.

    :param session: A Session object that can be used for communication.
    :type session: keystoneauth1.session.Session
    :param string url: Endpoint or discovery URL from which to retrieve data.
    :param bool authenticated: Include a token in the discovery call.
                               (optional) Defaults to None.
    :return: A list of dicts containing version information.
    :rtype: list(dict)
    """
    headers = {'Accept': 'application/json'}

    try:
        resp = session.get(url, headers=headers, authenticated=authenticated)
    except exceptions.Unauthorized:
        resp = session.get(url, headers=headers, authenticated=True)

    try:
        body_resp = resp.json()
    except ValueError:
        pass
    else:
        # Swift returns the list of containers for an account on an
        # authenticated GET from /, not a version document. To our knowledge
        # it's the only thing returning a [] here - and that's ok.
        if isinstance(body_resp, list):
            raise exceptions.DiscoveryFailure(
                'Invalid Response - List returned instead of dict')

        # In the event of querying a root URL we will get back a list of
        # available versions.
        try:
            return body_resp['versions']['values']
        except (KeyError, TypeError):
            pass

        # Most servers don't have a 'values' element so accept a simple
        # versions dict if available.
        try:
            return body_resp['versions']
        except KeyError:
            pass

        # Otherwise if we query an endpoint like /v2.0 then we will get back
        # just the one available version.
        try:
            return [body_resp['version']]
        except KeyError:
            pass

        # Older Ironic does not actually return a discovery document for the
        # single version discovery endpoint, which confuses the single-version
        # fallback logic. While there are no known other services returning
        # min/max ranges using headers instead of body, this is done in a
        # non-Ironic specific manner just in case.
        # The existence of this support should not be an indication to any
        # OpenStack services that they should ADD this.
        if 'id' in body_resp:
            body_resp['status'] = Status.CURRENT
            for header in resp.headers:
                # We lose the case-insensitive quality here
                header = header.lower()
                if not header.startswith('x-openstack'):
                    continue
                # Once the body starts having these values, stop overriding
                # with the header values
                if header.endswith('api-minimum-version'):
                    body_resp.setdefault('min_version', resp.headers[header])
                if header.endswith('api-maximum-version'):
                    body_resp.setdefault('version', resp.headers[header])
            return [body_resp]

    err_text = resp.text[:50] + '...' if len(resp.text) > 50 else resp.text
    raise exceptions.DiscoveryFailure('Invalid Response - Bad version data '
                                      'returned: %s' % err_text)


def normalize_version_number(version):
    """Turn a version representation into a tuple.

    Examples:

    The following all produce a return value of (1, 0)::

      1, '1', 'v1', [1], (1,), ['1'], 1.0, '1.0', 'v1.0', (1, 0)

    The following all produce a return value of (1, 20, 3)::

      'v1.20.3', '1.20.3', (1, 20, 3), ['1', '20', '3']

    The following all produce a return value of (LATEST, LATEST)::

      'latest', 'vlatest', ('latest', 'latest'), (LATEST, LATEST)

    The following all produce a return value of (2, LATEST)::

      '2.latest', 'v2.latest', (2, LATEST), ('2', 'latest')

    :param version: A version specifier in any of the following forms:
        String, possibly prefixed with 'v', containing one or more numbers
        *or* the string 'latest', separated by periods.  Examples: 'v1',
        'v1.2', '1.2.3', '123', 'latest', '1.latest', 'v1.latest'.
        Integer.  This will be assumed to be the major version, with a minor
        version of 0.
        Float.  The integer part is assumed to be the major version; the
        decimal part the minor version.
        Non-string iterable comprising integers, integer strings, the string
        'latest', or the special value LATEST.
        Examples: (1,), [1, 2], ('12', '34', '56'), (LATEST,), (2, 'latest')
    :return: A tuple of len >= 2 comprising integers and/or LATEST.
    :raises TypeError: If the input version cannot be interpreted.
    """
    # Copy the input var so the error presents the original value
    ver = version

    # If it's a non-string iterable, turn it into a string for subsequent
    # processing.  This ensures at least 1 decimal point if e.g. [1] is given.
    if not isinstance(ver, six.string_types):
        try:
            ver = '.'.join(map(_str_or_latest, ver))
        except TypeError:
            # Not an iterable
            pass

    # If it's a numeric or an integer as a string then normalize it to a
    # float string. This ensures 1 decimal point.
    # If it's a float as a string, don't do that, the split/map below will do
    # what we want. (Otherwise, we wind up with 3.20 -> (3, 2))
    if isinstance(ver, six.string_types):
        # trim the v from a 'v2.0' or similar
        ver = ver.lstrip('v')
        try:
            # If version is a pure int, like '1' or '200' this will produce
            # a stringified version with a .0 added. If it's any other number,
            # such as '1.1' - int(version) raises an Exception
            ver = str(float(int(ver)))
        except ValueError:
            pass

    # If it's an int or float, turn it into a float string
    elif isinstance(ver, (int, float)):
        ver = _str_or_latest(float(ver))

    # At this point, we should either have a string that contains numbers with
    # at least one decimal point, or something decidedly else.

    # if it's a string from above break it on .
    try:
        ver = ver.split('.')
    except AttributeError:
        # Not a string
        pass

    # Handle special case variants of just 'latest'
    if ver == 'latest' or tuple(ver) == ('latest',):
        return LATEST, LATEST

    # It's either an interable, or something else that makes us sad.
    try:
        return tuple(map(_int_or_latest, ver))
    except (TypeError, ValueError):
        pass

    raise TypeError('Invalid version specified: %s' % version)


def _normalize_version_args(
        version, min_version, max_version, service_type=None):
    # The sins of our fathers become the blood on our hands.
    # If a user requests an old-style service type such as volumev2, then they
    # are inherently requesting the major API version 2. It's not a good
    # interface, but it's the one that was imposed on the world years ago
    # because the client libraries all hid the version discovery document.
    # In order to be able to ensure that a user who requests volumev2 does not
    # get a block-storage endpoint that only provides v3 of the block-storage
    # service, we need to pull the version out of the service_type. The
    # service-types-authority will prevent the growth of new monstrosities such
    # as this, but in order to move forward without breaking people, we have
    # to just cry in the corner while striking ourselves with thorned branches.
    # That said, for sure only do this hack for officially known service_types.
    if (service_type and
            _SERVICE_TYPES.is_known(service_type) and
            service_type[-1].isdigit() and
            service_type[-2] == 'v'):
        implied_version = normalize_version_number(service_type[-1])
    else:
        implied_version = None

    if version and (min_version or max_version):
        raise ValueError(
            "version is mutually exclusive with min_version and max_version")

    if version:
        # Explode this into min_version and max_version
        min_version = normalize_version_number(version)
        max_version = (min_version[0], LATEST)
        if implied_version:
            if min_version[0] != implied_version[0]:
                raise exceptions.ImpliedVersionMismatch(
                    service_type=service_type,
                    implied=implied_version,
                    given=version_to_string(version))
        return min_version, max_version

    if min_version == 'latest':
        if max_version not in (None, 'latest'):
            raise ValueError(
                "min_version is 'latest' and max_version is {max_version}"
                " but is only allowed to be 'latest' or None".format(
                    max_version=max_version))
        max_version = 'latest'

    # Normalize e.g. empty string to None
    min_version = min_version or None
    max_version = max_version or None

    if min_version:
        min_version = normalize_version_number(min_version)
        # If min_version was specified but max_version was not, max is latest.
        max_version = normalize_version_number(max_version or 'latest')

    # NOTE(efried): We should be doing this instead:
    # max_version = normalize_version_number(max_version or 'latest')
    # However, see first NOTE(jamielennox) in EndpointData._set_version_info.
    if max_version:
        max_version = normalize_version_number(max_version)

    if None not in (min_version, max_version) and max_version < min_version:
        raise ValueError("min_version cannot be greater than max_version")

    if implied_version:
        if min_version:
            if min_version[0] != implied_version[0]:
                raise exceptions.ImpliedMinVersionMismatch(
                    service_type=service_type,
                    implied=implied_version,
                    given=version_to_string(min_version))
        else:
            min_version = implied_version

        # If 'latest' is provided with a versioned service-type like
        # volumev2 - the user wants the latest of volumev2, not the latest
        # of block-storage.
        if max_version and max_version[0] != LATEST:
            if max_version[0] != implied_version[0]:
                raise exceptions.ImpliedMaxVersionMismatch(
                    service_type=service_type,
                    implied=implied_version,
                    given=version_to_string(max_version))
        else:
            max_version = (implied_version[0], LATEST)
    return min_version, max_version


def version_to_string(version):
    """Turn a version tuple into a string.

    :param tuple version: A version represented as a tuple of ints.  As a
                          special case, a tuple member may be LATEST, which
                          translates to 'latest'.
    :return: A version represented as a period-delimited string.
    """
    # Special case
    if all(ver == LATEST for ver in version):
        return 'latest'

    return ".".join(map(_str_or_latest, version))


def version_between(min_version, max_version, candidate):
    """Determine whether a candidate version is within a specified range.

    :param min_version: The minimum version that is acceptable.
                        None/empty indicates no lower bound.
    :param max_version: The maximum version that is acceptable.
                        None/empty indicates no upper bound.
    :param candidate: Candidate version to test.  May not be None/empty.
    :return: True if candidate is between min_version and max_version; False
             otherwise.
    :raises ValueError: If candidate is None.
    :raises TypeError: If any input cannot be normalized.
    """
    if not candidate:
        raise ValueError("candidate is required.")
    candidate = normalize_version_number(candidate)

    # Normalize up front to validate any malformed inputs
    if min_version:
        min_version = normalize_version_number(min_version)
    if max_version:
        max_version = normalize_version_number(max_version)

    # If the candidate is less than the min_version, it's not a match.
    # No min_version means no lower bound.
    if min_version and candidate < min_version:
        return False

    # If the candidate is higher than the max_version, it's not a match.
    # No max_version means no upper bound.
    if max_version and candidate > max_version:
        return False

    return True


def version_match(required, candidate):
    """Test that an available version satisfies the required version.

    To be suitable a version must be of the same major version as required
    and be at least a match in minor/patch level.

    eg. 3.3 is a match for a required 3.1 but 4.1 is not.

    :param tuple required: the version that must be met.
    :param tuple candidate: the version to test against required.

    :returns: True if candidate is suitable False otherwise.
    :rtype: bool
    """
    # major versions must be the same (e.g. even though v2 is a lower
    # version than v3 we can't use it if v2 was requested)
    if candidate[0] != required[0]:
        return False

    # prevent selecting a minor version less than what is required
    if candidate < required:
        return False

    return True


def _latest_soft_match(required, candidate):
    if not required:
        return False

    if LATEST not in required:
        return False

    if all(part == LATEST for part in required):
        return True

    if required[0] == candidate[0] and required[1] == LATEST:
        return True

    # TODO(efried): Do we need to handle >2-part version numbers here?

    return False


def _combine_relative_url(discovery_url, version_url):
    # NOTE(jamielennox): urllib.parse.urljoin allows the url to be relative
    # or even protocol-less. The additional trailing '/' makes urljoin respect
    # the current path as canonical even if the url doesn't include it. for
    # example a "v2" path from http://host/admin should resolve as
    # http://host/admin/v2 where it would otherwise be host/v2. This has no
    # effect on absolute urls.
    url = urllib.parse.urljoin(discovery_url.rstrip('/') + '/', version_url)

    # Sadly version discovery documents are common with the scheme
    # and netloc broken.
    parsed_version_url = urllib.parse.urlparse(url)
    parsed_discovery_url = urllib.parse.urlparse(discovery_url)

    # The services can override the version_url with some config options.(for
    # example, In Keystone, Cinder and Glance, the option is "public_endpoint",
    # and "compute_link_prefix", "network_link_prefix" in Nova and Neutron.
    # In this case, it's hard to distinguish which part in version_url is
    # useful for discovery_url , so here we just get the version from
    # version_url and then add it into the discovery_url if needed.
    path = parsed_version_url.path
    if parsed_discovery_url.netloc != parsed_version_url.netloc:
        version = version_url.rstrip('/').split('/')[-1]
        url_path = parsed_discovery_url.path.rstrip('/')
        if not url_path.endswith(version):
            path = url_path + '/' + version
            if version_url.endswith('/'):
                # add '/' back to keep backward compatibility.
                path = path + '/'
        else:
            path = parsed_discovery_url.path

    return urllib.parse.ParseResult(
        parsed_discovery_url.scheme,
        parsed_discovery_url.netloc,
        path,
        parsed_version_url.params,
        parsed_version_url.query,
        parsed_version_url.fragment).geturl()


def _version_from_url(url):
    if not url:
        return url

    url = urllib.parse.urlparse(url)
    for part in reversed(url.path.split('/')):
        try:
            # All integer project ids can parse as valid versions. In URLs
            # all known instances of versions start with a v. So check to make
            # sure the url part starts with 'v', then check that it parses
            # as a valid version.
            if part[0] != 'v':
                continue
            return normalize_version_number(part)
        except Exception:
            pass
    return None


class Status(object):
    CURRENT = 'CURRENT'
    SUPPORTED = 'SUPPORTED'
    DEPRECATED = 'DEPRECATED'
    EXPERIMENTAL = 'EXPERIMENTAL'
    UNKNOWN = 'UNKNOWN'
    KNOWN = (CURRENT, SUPPORTED, DEPRECATED, EXPERIMENTAL)

    @classmethod
    def normalize(cls, raw_status):
        """Turn a status into a canonical status value.

        If the status from the version discovery document does not match one
        of the known values, it will be set to 'UNKNOWN'.

        :param str raw_status: Status value from a discovery document.

        :returns: A canonicalized version of the status. Valid values
                  are CURRENT, SUPPORTED, DEPRECATED, EXPERIMENTAL and UNKNOWN
        :rtype: str
        """
        status = raw_status.upper()
        if status == 'STABLE':
            status = cls.CURRENT
        if status not in cls.KNOWN:
            status = cls.UNKNOWN
        return status


class Discover(object):

    CURRENT_STATUSES = ('stable', 'current', 'supported')
    DEPRECATED_STATUSES = ('deprecated',)
    EXPERIMENTAL_STATUSES = ('experimental',)

    def __init__(self, session, url, authenticated=None):
        self._url = url
        self._data = get_version_data(session, url,
                                      authenticated=authenticated)

    def raw_version_data(self, allow_experimental=False,
                         allow_deprecated=True, allow_unknown=False):
        """Get raw version information from URL.

        Raw data indicates that only minimal validation processing is performed
        on the data, so what is returned here will be the data in the same
        format it was received from the endpoint.

        :param bool allow_experimental: Allow experimental version endpoints.
        :param bool allow_deprecated: Allow deprecated version endpoints.
        :param bool allow_unknown: Allow endpoints with an unrecognised status.

        :returns: The endpoints returned from the server that match the
                  criteria.
        :rtype: list
        """
        versions = []
        for v in self._data:
            try:
                status = v['status']
            except KeyError:
                _LOGGER.warning('Skipping over invalid version data. '
                                'No stability status in version.')
                continue

            status = status.lower()

            if status in self.CURRENT_STATUSES:
                versions.append(v)
            elif status in self.DEPRECATED_STATUSES:
                if allow_deprecated:
                    versions.append(v)
            elif status in self.EXPERIMENTAL_STATUSES:
                if allow_experimental:
                    versions.append(v)
            elif allow_unknown:
                versions.append(v)

        return versions

    def version_data(self, reverse=False, **kwargs):
        """Get normalized version data.

        Return version data in a structured way.

        :param bool reverse: Reverse the list. reverse=true will mean the
                             returned list is sorted from newest to oldest
                             version.
        :returns: A list of :class:`VersionData` sorted by version number.
        :rtype: list(VersionData)
        """
        data = self.raw_version_data(**kwargs)
        versions = []

        for v in data:
            try:
                version_str = v['id']
            except KeyError:
                _LOGGER.info('Skipping invalid version data. Missing ID.')
                continue

            try:
                links = v['links']
            except KeyError:
                _LOGGER.info('Skipping invalid version data. Missing links')
                continue

            version_number = normalize_version_number(version_str)

            # collect microversion information
            # NOTE(efried): Some existing discovery documents (e.g. from nova
            # v2.0 in the pike release) include *version keys with "" (empty
            # string) values, expecting them to be treated the same as if the
            # keys were absent.
            min_microversion = v.get('min_version') or None
            if min_microversion:
                min_microversion = normalize_version_number(min_microversion)
            max_microversion = v.get('max_version')
            if not max_microversion:
                max_microversion = v.get('version') or None
            if max_microversion:
                max_microversion = normalize_version_number(max_microversion)
            next_min_version = v.get('next_min_version') or None
            if next_min_version:
                next_min_version = normalize_version_number(next_min_version)
            not_before = v.get('not_before') or None

            self_url = None
            collection_url = None
            for link in links:
                try:
                    rel = link['rel']
                    url = _combine_relative_url(self._url, link['href'])
                except (KeyError, TypeError):
                    _LOGGER.info('Skipping invalid version link. '
                                 'Missing link URL or relationship.')
                    continue

                if rel.lower() == 'self':
                    self_url = url
                elif rel.lower() == 'collection':
                    collection_url = url
            if not self_url:
                _LOGGER.info('Skipping invalid version data. '
                             'Missing link to endpoint.')
                continue

            versions.append(
                VersionData(version=version_number,
                            url=self_url,
                            collection=collection_url,
                            min_microversion=min_microversion,
                            max_microversion=max_microversion,
                            next_min_version=next_min_version,
                            not_before=not_before,
                            status=Status.normalize(v['status']),
                            raw_status=v['status']))

        versions.sort(key=lambda v: v['version'], reverse=reverse)
        return versions

    def version_string_data(self, reverse=False, **kwargs):
        """Get normalized version data with versions as strings.

        Return version data in a structured way.

        :param bool reverse: Reverse the list. reverse=true will mean the
                             returned list is sorted from newest to oldest
                             version.
        :returns: A list of :class:`VersionData` sorted by version number.
        :rtype: list(VersionData)
        """
        version_data = self.version_data(reverse=reverse, **kwargs)
        for version in version_data:
            for key in ('version', 'min_microversion', 'max_microversion'):
                if version[key]:
                    version[key] = version_to_string(version[key])
        return version_data

    def data_for(self, version, **kwargs):
        """Return endpoint data for a version.

        NOTE: This method raises a TypeError if version is None. It is
              kept for backwards compatability. New code should use
              versioned_data_for instead.

        :param tuple version: The version is always a minimum version in the
            same major release as there should be no compatibility issues with
            using a version newer than the one asked for.

        :returns: the endpoint data for a URL that matches the required version
                  (the format is described in version_data) or None if no
                  match.
        :rtype: dict
        """
        version = normalize_version_number(version)

        for data in self.version_data(reverse=True, **kwargs):
            # Since the data is reversed, the latest version is first.  If
            # latest was requested, return it.
            if _latest_soft_match(version, data['version']):
                return data
            if version_match(version, data['version']):
                return data

        return None

    def url_for(self, version, **kwargs):
        """Get the endpoint url for a version.

        NOTE: This method raises a TypeError if version is None. It is
              kept for backwards compatability. New code should use
              versioned_url_for instead.

        :param tuple version: The version is always a minimum version in the
            same major release as there should be no compatibility issues with
            using a version newer than the one asked for.

        :returns: The url for the specified version or None if no match.
        :rtype: str
        """
        data = self.data_for(version, **kwargs)
        return data['url'] if data else None

    def versioned_data_for(self, url=None,
                           min_version=None, max_version=None,
                           **kwargs):
        """Return endpoint data for the service at a url.

        min_version and max_version can be given either as strings or tuples.

        :param string url: If url is given, the data will be returned for the
            endpoint data that has a self link matching the url.
        :param min_version: The minimum endpoint version that is acceptable. If
            min_version is given with no max_version it is as if max version is
            'latest'. If min_version is 'latest', max_version may only be
            'latest' or None.
        :param max_version: The maximum endpoint version that is acceptable. If
            min_version is given with no max_version it is as if max version is
            'latest'. If min_version is 'latest', max_version may only be
            'latest' or None.

        :returns: the endpoint data for a URL that matches the required version
                  (the format is described in version_data) or None if no
                  match.
        :rtype: dict
        """
        min_version, max_version = _normalize_version_args(
            None, min_version, max_version)
        no_version = not max_version and not min_version

        version_data = self.version_data(reverse=True, **kwargs)

        # If we don't have to check a min_version, we can short
        # circuit anything else
        if (max_version == (LATEST, LATEST) and
                (not min_version or min_version == (LATEST, LATEST))):
            # because we reverse we can just take the first entry
            return version_data[0]

        if url:
            url = url.rstrip('/') + '/'

        if no_version and not url:
            # because we reverse we can just take the first entry
            return version_data[0]

        # Version data is in order from highest to lowest, so we return
        # the first matching entry
        for data in version_data:
            if url and data['url'] and data['url'].rstrip('/') + '/' == url:
                return data
            if _latest_soft_match(min_version, data['version']):
                return data
            # Only validate version bounds if versions were specified
            if min_version and max_version and version_between(
                    min_version, max_version, data['version']):
                return data

        # If there is no version requested and we could not find a matching
        # url in the discovery doc, that means we've got an unversioned
        # endpoint in the catalog and the user is requesting version data
        # so that they know what version they got. We can return the first
        # entry from version_data, because the user hasn't requested anything
        # different.
        if no_version and url and len(version_data) > 0:
            return version_data[0]

        # We couldn't find a match.
        return None

    def versioned_url_for(self, min_version=None, max_version=None, **kwargs):
        """Get the endpoint url for a version.

        min_version and max_version can be given either as strings or tuples.

        :param min_version: The minimum version that is acceptable. If
            min_version is given with no max_version it is as if max version
            is 'latest'.
        :param max_version: The maximum version that is acceptable. If
            min_version is given with no max_version it is as if max version is
            'latest'.

        :returns: The url for the specified version or None if no match.
        :rtype: str
        """
        data = self.versioned_data_for(min_version=min_version,
                                       max_version=max_version, **kwargs)
        return data['url'] if data else None


class VersionData(dict):
    """Normalized Version Data about an endpoint."""

    def __init__(
            self,
            version,
            url,
            collection=None,
            max_microversion=None,
            min_microversion=None,
            next_min_version=None,
            not_before=None,
            status='CURRENT',
            raw_status=None):
        super(VersionData, self).__init__()
        self['version'] = version
        self['url'] = url
        self['collection'] = collection
        self['max_microversion'] = max_microversion
        self['min_microversion'] = min_microversion
        self['next_min_version'] = next_min_version
        self['not_before'] = not_before
        self['status'] = status
        self['raw_status'] = raw_status

    @property
    def version(self):
        """The normalized version of the endpoint."""
        return self.get('version')

    @property
    def url(self):
        """The url for the endpoint."""
        return self.get('url')

    @property
    def collection(self):
        """The URL for the discovery document.

        May be None.
        """
        return self.get('collection')

    @property
    def min_microversion(self):
        """The minimum microversion supported by the endpoint.

        May be None.
        """
        return self.get('min_microversion')

    @property
    def max_microversion(self):
        """The maximum microversion supported by the endpoint.

        May be None.
        """
        return self.get('max_microversion')

    @property
    def status(self):
        """A canonicalized version of the status.

        Valid values are CURRENT, SUPPORTED, DEPRECATED and EXPERIMENTAL.
        """
        return self.get('status')

    @property
    def raw_status(self):
        """The status as provided by the server."""
        return self.get('raw_status')


class EndpointData(object):
    """Normalized information about a discovered endpoint.

    Contains url, version, microversion, interface and region information.
    This is essentially the data contained in the catalog and the version
    discovery documents about an endpoint that is used to select the endpoint
    desired by the user. It is returned so that a user can know which qualities
    a discovered endpoint had, in case their request allowed for a range of
    possibilities.
    """

    def __init__(self,
                 catalog_url=None,
                 service_url=None,
                 service_type=None,
                 service_name=None,
                 service_id=None,
                 region_name=None,
                 interface=None,
                 endpoint_id=None,
                 raw_endpoint=None,
                 api_version=None,
                 major_version=None,
                 min_microversion=None,
                 max_microversion=None,
                 next_min_version=None,
                 not_before=None,
                 status=None):
        self.catalog_url = catalog_url
        self.service_url = service_url
        self.service_type = service_type
        self.service_name = service_name
        self.service_id = service_id
        self.interface = interface
        self.region_name = region_name
        self.endpoint_id = endpoint_id
        self.raw_endpoint = raw_endpoint
        self.major_version = major_version
        self.min_microversion = min_microversion
        self.max_microversion = max_microversion
        self.next_min_version = next_min_version
        self.not_before = not_before
        self.status = status
        self._saved_project_id = None
        self._catalog_matches_version = False
        self._catalog_matches_exactly = False
        self._disc = None

        self.api_version = api_version or _version_from_url(self.url)

    def __copy__(self):
        """Return a new EndpointData based on this one."""
        new_data = EndpointData(
            catalog_url=self.catalog_url,
            service_url=self.service_url,
            service_type=self.service_type,
            service_name=self.service_name,
            service_id=self.service_id,
            region_name=self.region_name,
            interface=self.interface,
            endpoint_id=self.endpoint_id,
            raw_endpoint=self.raw_endpoint,
            api_version=self.api_version,
            major_version=self.major_version,
            min_microversion=self.min_microversion,
            max_microversion=self.max_microversion,
            next_min_version=self.next_min_version,
            not_before=self.not_before,
            status=self.status,
        )
        # Save cached discovery object - but we don't want to
        # actually provide a constructor argument
        new_data._disc = self._disc
        new_data._saved_project_id = self._saved_project_id
        return new_data

    def __str__(self):
        """Produce a string like EndpointData{key=val, ...}, for debugging."""
        str_attrs = (
            'api_version', 'catalog_url', 'endpoint_id', 'interface',
            'major_version', 'max_microversion', 'min_microversion',
            'next_min_version', 'not_before', 'raw_endpoint', 'region_name',
            'service_id', 'service_name', 'service_type', 'service_url', 'url')
        return "%s{%s}" % (self.__class__.__name__, ', '.join(
            ["%s=%s" % (attr, getattr(self, attr)) for attr in str_attrs]))

    @property
    def url(self):
        return self.service_url or self.catalog_url

    def get_current_versioned_data(self, session, allow=None, cache=None,
                                   project_id=None):
        """Run version discovery on the current endpoint.

        A simplified version of get_versioned_data, get_current_versioned_data
        runs discovery but only on the endpoint that has been found already.

        It can be useful in some workflows where the user wants version
        information about the endpoint they have.

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session
        :param dict allow: Extra filters to pass when discovering API
                           versions. (optional)
        :param dict cache: A dict to be used for caching results in
                           addition to caching them on the Session.
                           (optional)
        :param string project_id: ID of the currently scoped project. Used for
                                  removing project_id components of URLs from
                                  the catalog. (optional)

        :returns: A new EndpointData with the requested versioned data.
        :rtype: :py:class:`keystoneauth1.discover.EndpointData`
        :raises keystoneauth1.exceptions.discovery.DiscoveryFailure: If the
                                                    appropriate versioned data
                                                    could not be discovered.
        """
        min_version, max_version = _normalize_version_args(
            self.api_version, None, None)
        return self.get_versioned_data(
            session=session, allow=allow, cache=cache, allow_version_hack=True,
            discover_versions=True,
            min_version=min_version, max_version=max_version)

    def get_versioned_data(self, session, allow=None, cache=None,
                           allow_version_hack=True, project_id=None,
                           discover_versions=True,
                           min_version=None, max_version=None):
        """Run version discovery for the service described.

        Performs Version Discovery and returns a new EndpointData object with
        information found.

        min_version and max_version can be given either as strings or tuples.

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session
        :param dict allow: Extra filters to pass when discovering API
                           versions. (optional)
        :param dict cache: A dict to be used for caching results in
                           addition to caching them on the Session.
                           (optional)
        :param bool allow_version_hack: Allow keystoneauth to hack up catalog
                                        URLS to support older schemes.
                                        (optional, default True)
        :param string project_id: ID of the currently scoped project. Used for
                                  removing project_id components of URLs from
                                  the catalog. (optional)
        :param bool discover_versions: Whether to get version metadata from
                                       the version discovery document even
                                       if it's not neccessary to fulfill the
                                       major version request. (optional,
                                       defaults to True)
        :param min_version: The minimum version that is acceptable. If
                            min_version is given with no max_version it is as
                            if max version is 'latest'.
        :param max_version: The maximum version that is acceptable. If
                            min_version is given with no max_version it is as
                            if max version is 'latest'.

        :returns: A new EndpointData with the requested versioned data.
        :rtype: :py:class:`keystoneauth1.discover.EndpointData`
        :raises keystoneauth1.exceptions.discovery.DiscoveryFailure: If the
                                                    appropriate versioned data
                                                    could not be discovered.
        """
        min_version, max_version = _normalize_version_args(
            None, min_version, max_version)

        if not allow:
            allow = {}

        # This method should always return a new EndpointData
        new_data = copy.copy(self)

        new_data._set_version_info(
            session=session, allow=allow, cache=cache,
            allow_version_hack=allow_version_hack, project_id=project_id,
            discover_versions=discover_versions, min_version=min_version,
            max_version=max_version)
        return new_data

    def get_all_version_string_data(self, session, project_id=None):
        """Return version data for all versions discovery can find.

        :param string project_id: ID of the currently scoped project. Used for
                                  removing project_id components of URLs from
                                  the catalog. (optional)
        :returns: A list of :class:`VersionData` sorted by version number.
        :rtype: list(VersionData)
        """
        versions = []
        for vers_url in self._get_discovery_url_choices(project_id=project_id):
            try:
                d = get_discovery(session, vers_url)
            except Exception as e:
                # Ignore errors here - we're just searching for one of the
                # URLs that will give us data.
                _LOGGER.debug(
                    "Failed attempt at discovery on %s: %s", vers_url, str(e))
                continue
            for version in d.version_string_data():
                versions.append(version)
            break
        return versions or self._infer_version_data(project_id)

    def _infer_version_data(self, project_id=None):
        """Return version data dict for when discovery fails.

        :param string project_id: ID of the currently scoped project. Used for
                                  removing project_id components of URLs from
                                  the catalog. (optional)
        :returns: A list of :class:`VersionData` sorted by version number.
        :rtype: list(VersionData)
        """
        version = self.api_version
        if version:
            version = version_to_string(self.api_version)

        url = self.url.rstrip("/")
        if project_id and url.endswith(project_id):
            url, _ = self.url.rsplit('/', 1)
        url += "/"

        return [VersionData(url=url, version=version)]

    def _set_version_info(self, session, allow=None, cache=None,
                          allow_version_hack=True, project_id=None,
                          discover_versions=False,
                          min_version=None, max_version=None):
        match_url = None

        no_version = not max_version and not min_version
        if no_version and not discover_versions:
            # NOTE(jamielennox): This may not be the best thing to default to
            # but is here for backwards compatibility. It may be worth
            # defaulting to the most recent version.
            return
        elif no_version and discover_versions:
            # We want to run discovery, but we don't want to find different
            # endpoints than what's in the catalog
            allow_version_hack = False
            match_url = self.url

        if project_id:
            self.project_id = project_id
        discovered_data = None
        # Maybe we've run discovery in the past and have a document that can
        # satisfy the request without further work
        if self._disc:
            discovered_data = self._disc.versioned_data_for(
                min_version=min_version, max_version=max_version,
                url=match_url, **allow)
        if not discovered_data:
            self._run_discovery(
                session=session, cache=cache,
                min_version=min_version, max_version=max_version,
                project_id=project_id, allow_version_hack=allow_version_hack,
                discover_versions=discover_versions)
            if not self._disc:
                return
            discovered_data = self._disc.versioned_data_for(
                min_version=min_version, max_version=max_version,
                url=match_url, **allow)

        if not discovered_data:
            if min_version and not max_version:
                raise exceptions.DiscoveryFailure(
                    "Minimum version {min_version} was not found".format(
                        min_version=version_to_string(min_version)))
            elif max_version and not min_version:
                raise exceptions.DiscoveryFailure(
                    "Maximum version {max_version} was not found".format(
                        max_version=version_to_string(max_version)))
            elif min_version and max_version:
                raise exceptions.DiscoveryFailure(
                    "No version found between {min_version}"
                    " and {max_version}".format(
                        min_version=version_to_string(min_version),
                        max_version=version_to_string(max_version)))
            else:
                raise exceptions.DiscoveryFailure(
                    "No version data found remotely at all")

        self.min_microversion = discovered_data['min_microversion']
        self.max_microversion = discovered_data['max_microversion']
        self.next_min_version = discovered_data['next_min_version']
        self.not_before = discovered_data['not_before']
        self.api_version = discovered_data['version']
        self.status = discovered_data['status']

        # TODO(mordred): these next two things should be done by Discover
        # in versioned_data_for.
        discovered_url = discovered_data['url']

        # NOTE(jamielennox): urljoin allows the url to be relative or even
        # protocol-less. The additional trailing '/' make urljoin respect
        # the current path as canonical even if the url doesn't include it.
        # for example a "v2" path from http://host/admin should resolve as
        # http://host/admin/v2 where it would otherwise be host/v2.
        # This has no effect on absolute urls returned from url_for.
        url = urllib.parse.urljoin(self._disc._url.rstrip('/') + '/',
                                   discovered_url)

        # If we had to pop a project_id from the catalog_url, put it back on
        if self._saved_project_id:
            url = urllib.parse.urljoin(url.rstrip('/') + '/',
                                       self._saved_project_id)
        self.service_url = url

    def _run_discovery(self, session, cache, min_version, max_version,
                       project_id, allow_version_hack, discover_versions):
        tried = set()

        for vers_url in self._get_discovery_url_choices(
                project_id=project_id,
                allow_version_hack=allow_version_hack,
                min_version=min_version,
                max_version=max_version):

            if self._catalog_matches_exactly and not discover_versions:
                # The version we started with is correct, and we don't want
                # new data
                return

            if vers_url in tried:
                continue
            tried.add(vers_url)

            try:
                self._disc = get_discovery(
                    session, vers_url,
                    cache=cache,
                    authenticated=False)
                break
            except (exceptions.DiscoveryFailure,
                    exceptions.HttpError,
                    exceptions.ConnectionError):
                continue
        if not self._disc:
            # We couldn't find a version discovery document anywhere.
            if self._catalog_matches_version:
                # But - the version in the catalog is fine.
                self.service_url = self.catalog_url
                return

            # NOTE(jamielennox): The logic here is required for backwards
            # compatibility. By itself it is not ideal.
            if allow_version_hack:
                # NOTE(jamielennox): If we can't contact the server we
                # fall back to just returning the URL from the catalog.  This
                # is backwards compatible behaviour and used when there is no
                # other choice. Realistically if you have provided a version
                # you should be able to rely on that version being returned or
                # the request failing.
                _LOGGER.warning(
                    'Failed to contact the endpoint at %s for '
                    'discovery. Fallback to using that endpoint as '
                    'the base url.', self.url)
                return

            else:
                # NOTE(jamielennox): If you've said no to allow_version_hack
                # and we can't determine the actual URL this is a failure
                # because we are specifying that the deployment must be up to
                # date enough to properly specify a version and keystoneauth
                # can't deliver.
                raise exceptions.DiscoveryFailure(
                    "Version requested but version discovery document was not"
                    " found and allow_version_hack was False")

    def _get_discovery_url_choices(
            self, project_id=None, allow_version_hack=True,
            min_version=None, max_version=None):
        """Find potential locations for version discovery URLs.

        min_version and max_version are already normalized, so will either be
        None or a tuple.
        """
        url = urllib.parse.urlparse(self.url.rstrip('/'))
        url_parts = url.path.split('/')

        # First, check to see if the catalog url ends with a project id
        # We need to remove it and save it for later if it does
        if project_id and url_parts[-1].endswith(project_id):
            self._saved_project_id = url_parts.pop()
        elif not project_id:
            # Peek to see if -2 is a version. If so, -1 is a project_id,
            # even if we don't know that at this point in the call stack
            try:
                normalize_version_number(url_parts[-2])
                self._saved_project_id = url_parts.pop()
            except (IndexError, TypeError):
                pass

        catalog_discovery = versioned_discovery = None

        # Next, check to see if the url indicates a version and if that
        # version either matches our version request or is within the
        # range requested. If so, we can start by trying the given url
        # as it has a high potential for success.
        try:
            url_version = normalize_version_number(url_parts[-1])
            versioned_discovery = urllib.parse.ParseResult(
                url.scheme,
                url.netloc,
                '/'.join(url_parts),
                url.params,
                url.query,
                url.fragment).geturl()
        except TypeError:
            pass
        else:
            # `is_between` means version bounds were specified *and* the URL
            # version is between them.
            is_between = min_version and max_version and version_between(
                min_version, max_version, url_version)
            exact_match = (is_between and max_version and
                           max_version[0] == url_version[0])
            high_match = (is_between and max_version and
                          max_version[1] != LATEST and
                          version_match(max_version, url_version))
            if exact_match or is_between:
                self._catalog_matches_version = True
                self._catalog_matches_exactly = exact_match
                # The endpoint from the catalog matches the version request
                # We construct a URL minus any project_id, but we don't
                # return it just yet. It's a good option, but unless we
                # have an exact match or match the max requested, we want
                # to try for an unversioned endpoint first.
                catalog_discovery = urllib.parse.ParseResult(
                    url.scheme,
                    url.netloc,
                    '/'.join(url_parts),
                    url.params,
                    url.query,
                    url.fragment).geturl().rstrip('/') + '/'

            # If we found a viable catalog endpoint and it's
            # an exact match or matches the max, go ahead and give
            # it a go.
            if catalog_discovery and (high_match or exact_match):
                yield catalog_discovery
                catalog_discovery = None

            url_parts.pop()

        if allow_version_hack:
            # If there were projects or versions in the url they are now gone.
            # That means we're left with what should be the unversioned url.
            hacked_url = urllib.parse.ParseResult(
                url.scheme,
                url.netloc,
                '/'.join(url_parts),
                url.params,
                url.query,
                url.fragment).geturl()
            # Since this is potentially us constructing a base URL from the
            # versioned URL - we need to make sure it has a trailing /. But
            # we only want to do that if we have built a new URL - not if
            # we're using the one from the catalog
            if hacked_url != self.catalog_url:
                hacked_url = hacked_url.strip('/') + '/'
            yield hacked_url

            # If we have a catalog discovery url, it either means we didn't
            # return it earlier because it wasn't an exact enough match, or
            # that we did and it failed. We don't double-request things when
            # consuming this, so it's safe to return it here in case we didn't
            # already return it.
            if catalog_discovery:
                yield catalog_discovery

            # NOTE(mordred): For backwards compatibility people might have
            # added version hacks using the version hack system. The logic
            # above should handle most cases, so by the time we get here it's
            # most likely to be a no-op
            yield self._get_catalog_discover_hack()
        elif versioned_discovery and self._saved_project_id:
            # We popped a project_id but are either avoiding version hacks
            # or we didn't request a version. That means we still want to fetch
            # the document from the "catalog url" - but the catalog url is has
            # a project_id suffix so is likely not going to work for us. Try
            # fetching from the project-less versioned endpoint.
            yield versioned_discovery

        # As a final fallthrough case, return the actual unmodified url from
        # the catalog.
        yield self.catalog_url

    def _get_catalog_discover_hack(self):
        """Apply the catalog hacks and figure out an unversioned endpoint.

        This function is internal to keystoneauth1.

        :returns: A url that has been transformed by the regex hacks that
                  match the service_type.
        """
        return _VERSION_HACKS.get_discover_hack(self.service_type, self.url)


def get_discovery(session, url, cache=None, authenticated=False):
    """Return the discovery object for a URL.

    Check the session and the plugin cache to see if we have already
    performed discovery on the URL and if so return it, otherwise create
    a new discovery object, cache it and return it.

    NOTE: This function is expected to be used by keystoneauth and should not
    be needed by users part of normal usage. A normal user should use
    get_endpoint or get_endpoint_data on `keystoneauth.session.Session` or
    endpoint_filters on `keystoneauth.session.Session` or
    `keystoneauth.session.Session`. However, should the user need to perform
    direct discovery for some reason, this function should be used so that
    the discovery caching is used.

    :param session: A session object to discover with.
    :type session: keystoneauth1.session.Session
    :param str url: The url to lookup.
    :param dict cache:
        A dict to be used for caching results, in addition to caching them
        on the Session. (optional) Defaults to None.
    :param bool authenticated:
        Include a token in the discovery call. (optional) Defaults to None,
        which will use a token if an auth plugin is installed.

    :raises keystoneauth1.exceptions.discovery.DiscoveryFailure:
        if for some reason the lookup fails.
    :raises keystoneauth1.exceptions.http.HttpError:
        An error from an invalid HTTP response.

    :returns: A discovery object with the results of looking up that URL.
    :rtype: :py:class:`keystoneauth1.discover.Discovery`
    """
    # There are between one and three different caches. The user may have
    # passed one in. There is definitely one on the session, and there is
    # one on the auth plugin if the Session has an auth plugin.
    caches = []

    # If a cache was passed in, check it first.
    if cache is not None:
        caches.append(cache)

    # If the session has a cache, check it second, since it could have been
    # provided by the user at Session creation time.
    if hasattr(session, '_discovery_cache'):
        caches.append(session._discovery_cache)

    # Finally check the auth cache associated with the Session.
    if session.auth and hasattr(session.auth, '_discovery_cache'):
        caches.append(session.auth._discovery_cache)

    # https://example.com and https://example.com/ should be treated the same
    # for caching purposes.
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.path in ('', '/'):
        url = urllib.parse.ParseResult(
            parsed_url.scheme,
            parsed_url.netloc,
            '',
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment).geturl()

    for cache in caches:
        disc = cache.get(url)

        if disc:
            break
    else:
        disc = Discover(session, url, authenticated=authenticated)

    # Whether we get one from fetching or from cache, set it in the
    # caches. This assures that if we combine sessions and auth plugins
    # that we don't make unnecessary calls.
    if disc:
        for cache in caches:
            cache[url] = disc

    return disc


class _VersionHacks(object):
    """A container to abstract the list of version hacks.

    This could be done as simply a dictionary but is abstracted like this to
    make for easier testing.
    """

    def __init__(self):
        self._discovery_data = {}

    def add_discover_hack(self, service_type, old, new=''):
        """Add a new hack for a service type.

        :param str service_type: The service_type in the catalog.
        :param re.RegexObject old: The pattern to use.
        :param str new: What to replace the pattern with.
        """
        hacks = self._discovery_data.setdefault(service_type, [])
        hacks.append((old, new))

    def get_discover_hack(self, service_type, url):
        """Apply the catalog hacks and figure out an unversioned endpoint.

        :param str service_type: the service_type to look up.
        :param str url: The original url that came from a service_catalog.

        :returns: Either the unversioned url or the one from the catalog
                  to try.
        """
        for old, new in self._discovery_data.get(service_type, []):
            new_string, number_of_subs_made = old.subn(new, url)
            if number_of_subs_made > 0:
                return new_string

        return url


_VERSION_HACKS = _VersionHacks()
_VERSION_HACKS.add_discover_hack('identity', re.compile('/v2.0/?$'), '/')


def add_catalog_discover_hack(service_type, old, new):
    """Add a version removal rule for a particular service.

    Originally deployments of OpenStack would contain a versioned endpoint in
    the catalog for different services. E.g. an identity service might look
    like ``http://localhost:5000/v2.0``. This is a problem when we want to use
    a different version like v3.0 as there is no way to tell where it is
    located. We cannot simply change all service catalogs either so there must
    be a way to handle the older style of catalog.

    This function adds a rule for a given service type that if part of the URL
    matches a given regular expression in *old* then it will be replaced with
    the *new* value. This will replace all instances of old with new. It should
    therefore contain a regex anchor.

    For example the included rule states::

        add_catalog_version_hack('identity', re.compile('/v2.0/?$'), '/')

    so if the catalog retrieves an *identity* URL that ends with /v2.0 or
    /v2.0/ then it should replace it simply with / to fix the user's catalog.

    :param str service_type: The service type as defined in the catalog that
                             the rule will apply to.
    :param re.RegexObject old: The regular expression to search for and replace
                               if found.
    :param str new: The new string to replace the pattern with.
    """
    _VERSION_HACKS.add_discover_hack(service_type, old, new)
