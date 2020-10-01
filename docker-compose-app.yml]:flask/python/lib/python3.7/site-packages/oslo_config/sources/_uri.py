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
r"""
Remote File
-----------

The **remote_file** backend driver is the first driver implemented by
oslo.config. It extends the previous limit of only accessing local files
to a new scenario where it is possible to access configuration data over
the network. The **remote_file** driver is based on the **requests** module
and is capable of accessing remote files through **HTTP** or **HTTPS**.

To definition of a remote_file configuration data source can be as minimal as::

    [DEFAULT]
    config_source = external_config_group

    [external_config_group]
    driver = remote_file
    uri = http://mydomain.com/path/to/config/data.conf

Or as complete as::

    [DEFAULT]
    config_source = external_config_group

    [external_config_group]
    driver = remote_file
    uri = https://mydomain.com/path/to/config/data.conf
    ca_path = /path/to/server/ca.pem
    client_key = /path/to/my/key.pem
    client_cert = /path/to/my/cert.pem

On the following sessions, you can find more information about this driver's
classes and its options.

The Driver Class
================

.. autoclass:: URIConfigurationSourceDriver

The Configuration Source Class
==============================

.. autoclass:: URIConfigurationSource

"""

import requests
import tempfile

from oslo_config import cfg
from oslo_config import sources


class URIConfigurationSourceDriver(sources.ConfigurationSourceDriver):
    """A backend driver for remote files served through http[s].

    Required options:
      - uri: URI containing the file location.

    Non-required options:
      - ca_path: The path to a CA_BUNDLE file or directory with
                 certificates of trusted CAs.

      - client_cert: Client side certificate, as a single file path
                     containing either the certificate only or the
                     private key and the certificate.

      - client_key: Client side private key, in case client_cert is
                    specified but does not includes the private key.
    """

    _uri_driver_opts = [
        cfg.URIOpt(
            'uri',
            schemes=['http', 'https'],
            required=True,
            sample_default='https://example.com/my-configuration.ini',
            help=('Required option with the URI of the '
                  'extra configuration file\'s location.'),
        ),
        cfg.StrOpt(
            'ca_path',
            sample_default='/etc/ca-certificates',
            help=('The path to a CA_BUNDLE file or directory '
                  'with certificates of trusted CAs.'),
        ),
        cfg.StrOpt(
            'client_cert',
            sample_default='/etc/ca-certificates/service-client-keystore',
            help=('Client side certificate, as a single file path '
                  'containing either the certificate only or the '
                  'private key and the certificate.'),
        ),
        cfg.StrOpt(
            'client_key',
            help=('Client side private key, in case client_cert is '
                  'specified but does not includes the private key.'),
        ),
    ]

    def list_options_for_discovery(self):
        return self._uri_driver_opts

    def open_source_from_opt_group(self, conf, group_name):
        conf.register_opts(self._uri_driver_opts, group_name)

        return URIConfigurationSource(
            conf[group_name].uri,
            conf[group_name].ca_path,
            conf[group_name].client_cert,
            conf[group_name].client_key)


class URIConfigurationSource(sources.ConfigurationSource):
    """A configuration source for remote files served through http[s].

    :param uri: The Uniform Resource Identifier of the configuration to be
          retrieved.

    :param ca_path: The path to a CA_BUNDLE file or directory with
              certificates of trusted CAs.

    :param client_cert: Client side certificate, as a single file path
                  containing either the certificate only or the
                  private key and the certificate.

    :param client_key: Client side private key, in case client_cert is
                 specified but does not includes the private key.
    """

    def __init__(self, uri, ca_path=None, client_cert=None, client_key=None):
        self._uri = uri
        self._namespace = cfg._Namespace(cfg.ConfigOpts())

        data = self._fetch_uri(uri, ca_path, client_cert, client_key)

        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.write(data.encode("utf-8"))
            tmpfile.flush()

            cfg.ConfigParser._parse_file(tmpfile.name, self._namespace)

    def _fetch_uri(self, uri, ca_path, client_cert, client_key):
        verify = ca_path if ca_path else True
        cert = (client_cert, client_key) if client_cert and client_key else \
            client_cert

        with requests.get(uri, verify=verify, cert=cert) as response:
            response.raise_for_status()  # raises only in case of HTTPError

            return response.text

    def get(self, group_name, option_name, opt):
        try:
            return self._namespace._get_value(
                [(group_name, option_name)],
                multi=opt.multi)
        except KeyError:
            return (sources._NoValue, None)
