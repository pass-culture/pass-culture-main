# Copyright 2011 OpenStack Foundation
# Copyright 2011, Piston Cloud Computing, Inc.
# Copyright 2011 Nebula, Inc.
#
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc
import copy

import six

from keystoneauth1 import discover
from keystoneauth1 import exceptions


@six.add_metaclass(abc.ABCMeta)
class ServiceCatalog(object):
    """Helper methods for dealing with a Keystone Service Catalog."""

    def __init__(self, catalog):
        self._catalog = catalog

    def _get_endpoint_region(self, endpoint):
        return endpoint.get('region_id') or endpoint.get('region')

    @property
    def catalog(self):
        """Return the raw service catalog content, mostly useful for debugging.

        Applications should avoid this and use accessor methods instead.
        However, there are times when inspecting the raw catalog can be useful
        for analysis and other reasons.
        """
        return self._catalog

    @abc.abstractmethod
    def is_interface_match(self, endpoint, interface):
        """Helper function to normalize endpoint matching across v2 and v3.

        :returns: True if the provided endpoint matches the required
                  interface otherwise False.
        """

    @staticmethod
    def normalize_interface(self, interface):
        """Handle differences in the way v2 and v3 catalogs specify endpoint.

        Both v2 and v3 must be able to handle the endpoint style of the other.
        For example v2 must be able to handle a 'public' interface and
        v3 must be able to handle a 'publicURL' interface.

        :returns: the endpoint string in the format appropriate for this
                  service catalog.
        """
        return interface

    def _normalize_endpoints(self, endpoints):
        """Translate endpoint description dicts into v3 form.

        Takes a raw endpoint description from the catalog and changes
        it to be in v3 format. It also saves a copy of the data in
        raw_endpoint so that it can be returned by methods that expect the
        actual original data.

        :param list endpoints: List of endpoint description dicts

        :returns: List of endpoint description dicts in v3 format
        """
        new_endpoints = []
        for endpoint in endpoints:
            raw_endpoint = endpoint.copy()
            new_endpoint = endpoint.copy()
            new_endpoint['raw_endpoint'] = raw_endpoint
            new_endpoints.append(new_endpoint)
        return new_endpoints

    def _denormalize_endpoints(self, endpoints):
        """Return original endpoint description dicts.

        Takes a list of EndpointData objects and returns the original
        dict that was returned from the catalog.

        :param list endpoints: List of `keystoneauth1.discover.EndpointData`

        :returns: List of endpoint description dicts in original catalog format
        """
        return [endpoint.raw_endpoint for endpoint in endpoints]

    def normalize_catalog(self):
        """Return the catalog normalized into v3 format."""
        catalog = []
        for service in copy.deepcopy(self._catalog):
            if 'type' not in service:
                continue

            # NOTE(jamielennox): service_name is different. It is not available
            # in API < v3.3. If it is in the catalog then we enforce it, if it
            # is not then we don't because the name could be correct we just
            # don't have that information to check against. Set to None so
            # that checks will naturally work.
            service.setdefault('name', None)

            # NOTE(jamielennox): there is no such thing as a service_id in v2
            # similarly to service_name.
            service.setdefault('id', None)

            service['endpoints'] = self._normalize_endpoints(
                service.get('endpoints', []))

            for endpoint in service['endpoints']:
                endpoint['region_name'] = self._get_endpoint_region(endpoint)
                endpoint.setdefault('id', None)
            catalog.append(service)
        return catalog

    def _get_interface_list(self, interface):
        if not interface:
            return []
        if not isinstance(interface, (list, tuple, set)):
            interface = [interface]
        return [self.normalize_interface(i) for i in interface]

    def get_endpoints_data(self, service_type=None, interface=None,
                           region_name=None, service_name=None,
                           service_id=None, endpoint_id=None):
        """Fetch and filter endpoint data for the specified service(s).

        Returns endpoints for the specified service (or all) containing
        the specified type (or all) and region (or all) and service name.

        If there is no name in the service catalog the service_name check will
        be skipped.  This allows compatibility with services that existed
        before the name was available in the catalog.

        Valid interface types: `public` or `publicURL`,
                               `internal` or `internalURL`,
                               `admin` or 'adminURL`

        :param string service_type: Service type of the endpoint.
        :param interface: Type of endpoint. Can be a single value or a list
                          of values. If it's a list of values, they will be
                          looked for in order of preference.
        :param string region_name: Region of the endpoint.
        :param string service_name: The assigned name of the service.
        :param string service_id: The identifier of a service.
        :param string endpoint_id: The identifier of an endpoint.

        :returns: a list of matching EndpointData objects
        :rtype: list(`keystoneauth1.discover.EndpointData`)

        :returns: a dict, keyed by service_type, of lists of EndpointData
        """
        interfaces = self._get_interface_list(interface)

        matching_endpoints = {}

        for service in self.normalize_catalog():

            if service_type and not discover._SERVICE_TYPES.is_match(
                    service_type, service['type']):
                continue

            if (service_name and service['name'] and
                    service_name != service['name']):
                continue

            if (service_id and service['id'] and
                    service_id != service['id']):
                continue

            matching_endpoints.setdefault(service['type'], [])

            for endpoint in service.get('endpoints', []):
                if interfaces and endpoint['interface'] not in interfaces:
                    continue
                if region_name and region_name != endpoint['region_name']:
                    continue
                if endpoint_id and endpoint_id != endpoint['id']:
                    continue
                if not endpoint['url']:
                    continue

                matching_endpoints[service['type']].append(
                    discover.EndpointData(
                        catalog_url=endpoint['url'],
                        service_type=service['type'],
                        service_name=service['name'],
                        service_id=service['id'],
                        interface=endpoint['interface'],
                        region_name=endpoint['region_name'],
                        endpoint_id=endpoint['id'],
                        raw_endpoint=endpoint['raw_endpoint']))

        if not interfaces:
            return self._endpoints_by_type(service_type, matching_endpoints)

        ret = {}
        for matched_service_type, endpoints in matching_endpoints.items():
            if not endpoints:
                ret[matched_service_type] = []
                continue
            matches_by_interface = {}
            for endpoint in endpoints:
                matches_by_interface.setdefault(endpoint.interface, [])
                matches_by_interface[endpoint.interface].append(endpoint)
            best_interface = [i for i in interfaces
                              if i in matches_by_interface.keys()][0]
            ret[matched_service_type] = matches_by_interface[best_interface]

        return self._endpoints_by_type(service_type, ret)

    def _endpoints_by_type(self, requested, endpoints):
        """Get the approrpriate endpoints from the list of given endpoints.

        Per the service type alias rules:

        If a user requests a service by its proper name and that matches, win.

        If a user requests a service by its proper name and only a single alias
        matches, win.

        If a user requests a service by its proper name and more than one alias
        matches, choose the first alias from the list given.

        Do the "first alias" match after the other filters, as they might limit
        the number of choices for us otherwise.

        :param str requested:
            The service_type as requested by the user.
        :param dict sc:
            A dictionary keyed by found service_type. Values are opaque to
            this method.

        :returns:
            Dict of service_type/endpoints filtered for the appropriate
            service_type based on alias matching rules.
        """
        if not requested or not discover._SERVICE_TYPES.is_known(requested):
            # The user did not request a service we have any alias information
            # about, or did not request a service, which means that we cannot
            # further filter the list.
            return endpoints

        if len(endpoints) < 2:
            # There is at most one type found from the initial pass through
            # the catalog. Nothing further to do.
            return endpoints

        # At this point, the user has requested a type, we do know things
        # about aliases for that type, and we've found more than one match.
        # We must filter out additional types, otherwise clouds that register
        # the same endpoint twice as part of a migration will confuse users.

        # Only return the one the user requested if there's an exact match
        # and there is data for it. There might not be data for this match
        # if there are other filters that excluded it from consideration
        # after we accepted it as an alias.
        if endpoints.get(requested):
            return {requested: endpoints[requested]}

        # We've matched something that isn't exactly what the user requested.
        # Look at the possible types for this service in order or priority and
        # return the first match.
        for alias in discover._SERVICE_TYPES.get_all_types(requested):
            if endpoints.get(alias):
                # Return the first one found in the order listed.
                return {alias: endpoints[alias]}

        # We should never get here - it's a programming logic error on our
        # part if we do. Raise this so that we can panic in unit tests.
        raise ValueError("Programming error choosing an endpoint.")

    def get_endpoints(self, service_type=None, interface=None,
                      region_name=None, service_name=None,
                      service_id=None, endpoint_id=None):
        """Fetch and filter endpoint data for the specified service(s).

        Returns endpoints for the specified service (or all) containing
        the specified type (or all) and region (or all) and service name.

        If there is no name in the service catalog the service_name check will
        be skipped.  This allows compatibility with services that existed
        before the name was available in the catalog.

        Returns a dict keyed by service_type with a list of endpoint dicts
        """
        endpoints_data = self.get_endpoints_data(
            service_type=service_type, interface=interface,
            region_name=region_name, service_name=service_name,
            service_id=service_id, endpoint_id=endpoint_id)
        endpoints = {}
        for service_type, data in endpoints_data.items():
            endpoints[service_type] = self._denormalize_endpoints(data)
        return endpoints

    def get_endpoint_data_list(self, service_type=None, interface='public',
                               region_name=None, service_name=None,
                               service_id=None, endpoint_id=None):
        """Fetch a flat list of matching EndpointData objects.

        Fetch the endpoints from the service catalog for a particular
        endpoint attribute. If no attribute is given, return the first
        endpoint of the specified type.

        Valid interface types: `public` or `publicURL`,
                               `internal` or `internalURL`,
                               `admin` or 'adminURL`

        :param string service_type: Service type of the endpoint.
        :param interface: Type of endpoint. Can be a single value or a list
                          of values. If it's a list of values, they will be
                          looked for in order of preference.
        :param string region_name: Region of the endpoint.
        :param string service_name: The assigned name of the service.
        :param string service_id: The identifier of a service.
        :param string endpoint_id: The identifier of an endpoint.

        :returns: a list of matching EndpointData objects
        :rtype: list(`keystoneauth1.discover.EndpointData`)
        """
        endpoints = self.get_endpoints_data(service_type=service_type,
                                            interface=interface,
                                            region_name=region_name,
                                            service_name=service_name,
                                            service_id=service_id,
                                            endpoint_id=endpoint_id)
        return [endpoint for data in endpoints.values() for endpoint in data]

    def get_urls(self, service_type=None, interface='public',
                 region_name=None, service_name=None,
                 service_id=None, endpoint_id=None):
        """Fetch endpoint urls from the service catalog.

        Fetch the urls of endpoints from the service catalog for a particular
        endpoint attribute. If no attribute is given, return the url of the
        first endpoint of the specified type.

        Valid interface types: `public` or `publicURL`,
                               `internal` or `internalURL`,
                               `admin` or 'adminURL`

        :param string service_type: Service type of the endpoint.
        :param interface: Type of endpoint. Can be a single value or a list
                          of values. If it's a list of values, they will be
                          looked for in order of preference.
        :param string region_name: Region of the endpoint.
        :param string service_name: The assigned name of the service.
        :param string service_id: The identifier of a service.
        :param string endpoint_id: The identifier of an endpoint.

        :returns: tuple of urls
        """
        endpoints = self.get_endpoint_data_list(service_type=service_type,
                                                interface=interface,
                                                region_name=region_name,
                                                service_name=service_name,
                                                service_id=service_id,
                                                endpoint_id=endpoint_id)
        return tuple([endpoint.url for endpoint in endpoints])

    def url_for(self, service_type=None, interface='public',
                region_name=None, service_name=None,
                service_id=None, endpoint_id=None):
        """Fetch an endpoint from the service catalog.

        Fetch the specified endpoint from the service catalog for
        a particular endpoint attribute. If no attribute is given, return
        the first endpoint of the specified type.

        Valid interface types: `public` or `publicURL`,
                               `internal` or `internalURL`,
                               `admin` or 'adminURL`

        :param string service_type: Service type of the endpoint.
        :param interface: Type of endpoint. Can be a single value or a list
                          of values. If it's a list of values, they will be
                          looked for in order of preference.
        :param string region_name: Region of the endpoint.
        :param string service_name: The assigned name of the service.
        :param string service_id: The identifier of a service.
        :param string endpoint_id: The identifier of an endpoint.
        """
        return self.endpoint_data_for(service_type=service_type,
                                      interface=interface,
                                      region_name=region_name,
                                      service_name=service_name,
                                      service_id=service_id,
                                      endpoint_id=endpoint_id).url

    def endpoint_data_for(self, service_type=None, interface='public',
                          region_name=None, service_name=None,
                          service_id=None, endpoint_id=None):
        """Fetch endpoint data from the service catalog.

        Fetch the specified endpoint data from the service catalog for
        a particular endpoint attribute. If no attribute is given, return
        the first endpoint of the specified type.

        Valid interface types: `public` or `publicURL`,
                               `internal` or `internalURL`,
                               `admin` or 'adminURL`

        :param string service_type: Service type of the endpoint.
        :param interface: Type of endpoint. Can be a single value or a list
                          of values. If it's a list of values, they will be
                          looked for in order of preference.
        :param string region_name: Region of the endpoint.
        :param string service_name: The assigned name of the service.
        :param string service_id: The identifier of a service.
        :param string endpoint_id: The identifier of an endpoint.
        """
        if not self._catalog:
            raise exceptions.EmptyCatalog('The service catalog is empty.')

        endpoint_data_list = self.get_endpoint_data_list(
            service_type=service_type,
            interface=interface,
            region_name=region_name,
            service_name=service_name,
            service_id=service_id,
            endpoint_id=endpoint_id)

        if endpoint_data_list:
            return endpoint_data_list[0]

        if service_name and region_name:
            msg = ('%(interface)s endpoint for %(service_type)s service '
                   'named %(service_name)s in %(region_name)s region not '
                   'found' %
                   {'interface': interface,
                    'service_type': service_type, 'service_name': service_name,
                    'region_name': region_name})
        elif service_name:
            msg = ('%(interface)s endpoint for %(service_type)s service '
                   'named %(service_name)s not found' %
                   {'interface': interface,
                    'service_type': service_type,
                    'service_name': service_name})
        elif region_name:
            msg = ('%(interface)s endpoint for %(service_type)s service '
                   'in %(region_name)s region not found' %
                   {'interface': interface,
                    'service_type': service_type, 'region_name': region_name})
        else:
            msg = ('%(interface)s endpoint for %(service_type)s service '
                   'not found' %
                   {'interface': interface,
                    'service_type': service_type})

        raise exceptions.EndpointNotFound(msg)


class ServiceCatalogV2(ServiceCatalog):
    """An object for encapsulating the v2 service catalog.

    The object is created using raw v2 auth token from Keystone.
    """

    @classmethod
    def from_token(cls, token):
        if 'access' not in token:
            raise ValueError('Invalid token format for fetching catalog')

        return cls(token['access'].get('serviceCatalog', {}))

    @staticmethod
    def normalize_interface(interface):
        if interface and 'URL' not in interface:
            interface += 'URL'

        return interface

    def is_interface_match(self, endpoint, interface):
        return interface in endpoint

    def _normalize_endpoints(self, endpoints):
        """Translate endpoint description dicts into v3 form.

        Takes a raw endpoint description from the catalog and changes
        it to be in v3 format. It also saves a copy of the data in
        raw_endpoint so that it can be returned by methods that expect the
        actual original data.

        :param list endpoints: List of endpoint description dicts

        :returns: List of endpoint description dicts in v3 format
        """
        new_endpoints = []
        for endpoint in endpoints:
            raw_endpoint = endpoint.copy()
            interface_urls = {}
            interface_keys = [key for key in endpoint.keys()
                              if key.endswith('URL')]
            for key in interface_keys:
                interface = self.normalize_interface(key)
                interface_urls[interface] = endpoint.pop(key)
            for interface, url in interface_urls.items():
                new_endpoint = endpoint.copy()
                new_endpoint['interface'] = interface
                new_endpoint['url'] = url
                # Save the actual endpoint for ease of later reconstruction
                new_endpoint['raw_endpoint'] = raw_endpoint
                new_endpoints.append(new_endpoint)
        return new_endpoints

    def _denormalize_endpoints(self, endpoints):
        """Return original endpoint description dicts.

        Takes a list of EndpointData objects and returns the original
        dict that was returned from the catalog.

        :param list endpoints: List of `keystoneauth1.discover.EndpointData`

        :returns: List of endpoint description dicts in original catalog format
        """
        raw_endpoints = super(ServiceCatalogV2, self)._denormalize_endpoints(
            endpoints)
        # The same raw endpoint content will be in the list once for each
        # v2 endpoint_type entry. We only need one of them in the resulting
        # list. So keep a list of the string versions.
        seen = {}
        endpoints = []
        for endpoint in raw_endpoints:
            if str(endpoint) in seen:
                continue
            seen[str(endpoint)] = True
            endpoints.append(endpoint)
        return endpoints


class ServiceCatalogV3(ServiceCatalog):
    """An object for encapsulating the v3 service catalog.

    The object is created using raw v3 auth token from Keystone.
    """

    @classmethod
    def from_token(cls, token):
        if 'token' not in token:
            raise ValueError('Invalid token format for fetching catalog')

        return cls(token['token'].get('catalog', {}))

    @staticmethod
    def normalize_interface(interface):
        if interface:
            interface = interface.rstrip('URL')

        return interface

    def is_interface_match(self, endpoint, interface):
        try:
            return interface == endpoint['interface']
        except KeyError:
            return False
