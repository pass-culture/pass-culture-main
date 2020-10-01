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

import os

from oslotest import base
from requests import HTTPError
import requests_mock
import testtools

from oslo_config import _list_opts
from oslo_config import cfg
from oslo_config import fixture
from oslo_config import sources
from oslo_config.sources import _uri


class TestProcessingSources(base.BaseTestCase):

    # NOTE(dhellmann): These tests use the config() method of the
    # fixture because that invokes set_override() on the option. The
    # load_raw_values() method injects data underneath the option, but
    # only after invoking __call__ on the ConfigOpts instance, which
    # is when the 'config_source' option is processed.

    def setUp(self):
        super(TestProcessingSources, self).setUp()
        self.conf = cfg.ConfigOpts()
        self.conf_fixture = self.useFixture(fixture.Config(self.conf))

    def test_no_sources_default(self):
        with base.mock.patch.object(
                self.conf,
                '_open_source_from_opt_group') as open_source:
            open_source.side_effect = AssertionError('should not be called')
            self.conf([])

    def test_no_sources(self):
        self.conf_fixture.config(
            config_source=[],
        )
        with base.mock.patch.object(
                self.conf,
                '_open_source_from_opt_group') as open_source:
            open_source.side_effect = AssertionError('should not be called')
            self.conf([])

    def test_source_named(self):
        self.conf_fixture.config(
            config_source=['missing_source'],
        )
        with base.mock.patch.object(
                self.conf,
                '_open_source_from_opt_group') as open_source:
            self.conf([])
            open_source.assert_called_once_with('missing_source')

    def test_multiple_sources_named(self):
        self.conf_fixture.config(
            config_source=['source1', 'source2'],
        )
        with base.mock.patch.object(
                self.conf,
                '_open_source_from_opt_group') as open_source:
            self.conf([])
            open_source.assert_has_calls([
                base.mock.call('source1'),
                base.mock.call('source2'),
            ])


class TestLoading(base.BaseTestCase):

    # NOTE(dhellmann): These tests can use load_raw_values() because
    # they explicitly call _open_source_from_opt_group() after the
    # ConfigOpts setup is done in __call__().

    def setUp(self):
        super(TestLoading, self).setUp()
        self.conf = cfg.ConfigOpts()
        self.conf_fixture = self.useFixture(fixture.Config(self.conf))

    def test_source_missing(self):
        # The group being loaded does not exist at all.
        source = self.conf._open_source_from_opt_group('missing_source')
        self.assertIsNone(source)

    def test_driver_missing(self):
        # The group exists and has other options, but does not specify
        # a driver.
        self.conf_fixture.load_raw_values(
            group='missing_driver',
            not_driver='foo',
        )
        source = self.conf._open_source_from_opt_group('missing_driver')
        self.assertIsNone(source)

    def test_unknown_driver(self):
        # The group exists, but does not specify a valid driver.
        self.conf_fixture.load_raw_values(
            group='unknown_driver',
            driver='very_unlikely_to_exist_driver_name',
        )
        source = self.conf._open_source_from_opt_group('unknown_driver')
        self.assertIsNone(source)


class TestEnvironmentConfigurationSource(base.BaseTestCase):

    def setUp(self):
        super(TestEnvironmentConfigurationSource, self).setUp()
        self.conf = cfg.ConfigOpts()
        self.conf_fixture = self.useFixture(fixture.Config(self.conf))
        self.conf.register_opt(cfg.StrOpt('bar'), 'foo')
        self.conf.register_opt(cfg.StrOpt('baz', regex='^[a-z].*$'), 'foo')

        def cleanup():
            for env in ('OS_FOO__BAR', 'OS_FOO__BAZ'):
                if env in os.environ:
                    del os.environ[env]

        self.addCleanup(cleanup)

    def test_simple_environment_get(self):
        self.conf(args=[])
        env_value = 'goodbye'
        os.environ['OS_FOO__BAR'] = env_value

        self.assertEqual(env_value, self.conf['foo']['bar'])

    def test_env_beats_files(self):
        file_value = 'hello'
        env_value = 'goodbye'
        self.conf(args=[])
        self.conf_fixture.load_raw_values(
            group='foo',
            bar=file_value,
        )

        self.assertEqual(file_value, self.conf['foo']['bar'])
        self.conf.reload_config_files()
        os.environ['OS_FOO__BAR'] = env_value
        self.assertEqual(env_value, self.conf['foo']['bar'])

    def test_cli_beats_env(self):
        env_value = 'goodbye'
        cli_value = 'cli'
        os.environ['OS_FOO__BAR'] = env_value
        self.conf.register_cli_opt(cfg.StrOpt('bar'), 'foo')
        self.conf(args=['--foo=%s' % cli_value])

        self.assertEqual(cli_value, self.conf['foo']['bar'])

    def test_use_env_false_allows_files(self):
        file_value = 'hello'
        env_value = 'goodbye'
        os.environ['OS_FOO__BAR'] = env_value
        self.conf(args=[], use_env=False)
        self.conf_fixture.load_raw_values(
            group='foo',
            bar=file_value,
        )

        self.assertEqual(file_value, self.conf['foo']['bar'])
        self.conf.reset()
        self.conf(args=[], use_env=True)
        self.assertEqual(env_value, self.conf['foo']['bar'])

    def test_invalid_env(self):
        self.conf(args=[])
        env_value = 'ABC'
        os.environ['OS_FOO__BAZ'] = env_value

        with testtools.ExpectedException(cfg.ConfigSourceValueError):
            self.conf['foo']['baz']


def make_uri(name):
    return "https://oslo.config/{}.conf".format(name)


_extra_configs = {
    make_uri("types"): {
        "name": "types",
        "data": {
            "DEFAULT": {
                "foo": (cfg.StrOpt, "bar")
            },
            "test": {
                "opt_str": (cfg.StrOpt, "a nice string"),
                "opt_bool": (cfg.BoolOpt, True),
                "opt_int": (cfg.IntOpt, 42),
                "opt_float": (cfg.FloatOpt, 3.14),
                "opt_ip": (cfg.IPOpt, "127.0.0.1"),
                "opt_port": (cfg.PortOpt, 443),
                "opt_host": (cfg.HostnameOpt, "www.openstack.org"),
                "opt_uri": (cfg.URIOpt, "https://www.openstack.org"),
                "opt_multi": (cfg.MultiStrOpt, ["abc", "def", "ghi"])
            }
        }
    },
    make_uri("ini_1"): {
        "name": "ini_1",
        "data": {
            "DEFAULT": {
                "abc": (cfg.StrOpt, "abc")
            }
        }
    },
    make_uri("ini_2"): {
        "name": "ini_2",
        "data": {
            "DEFAULT": {
                "abc": (cfg.StrOpt, "foo"),
                "def": (cfg.StrOpt, "def")
            }
        }
    },
    make_uri("ini_3"): {
        "name": "ini_3",
        "data": {
            "DEFAULT": {
                "abc": (cfg.StrOpt, "bar"),
                "def": (cfg.StrOpt, "bar"),
                "ghi": (cfg.StrOpt, "ghi")
            }
        }
    }
}


def opts_to_ini(uri, *args, **kwargs):
    opts = _extra_configs[uri]["data"]
    result = ""

    # 'g': group, 'o': option, 't': type, and 'v': value
    for g in opts.keys():
        result += "[{}]\n".format(g)
        for o, (t, v) in opts[g].items():
            if t == cfg.MultiStrOpt:
                for i in v:
                    result += "{} = {}\n".format(o, i)
            else:
                result += "{} = {}\n".format(o, v)

    return result


class URISourceTestCase(base.BaseTestCase):

    def setUp(self):
        super(URISourceTestCase, self).setUp()
        self.conf = cfg.ConfigOpts()
        self.conf_fixture = self.useFixture(fixture.Config(self.conf))

    def _register_opts(self, opts):
        # 'g': group, 'o': option, and 't': type
        for g in opts.keys():
            for o, (t, _) in opts[g].items():
                self.conf.register_opt(t(o), g if g != "DEFAULT" else None)

    def test_incomplete_driver(self):
        # The group exists, but does not specify the
        # required options for this driver.
        self.conf_fixture.load_raw_values(
            group='incomplete_ini_driver',
            driver='remote_file',
        )
        source = self.conf._open_source_from_opt_group('incomplete_ini_driver')
        self.assertIsNone(source)

    @requests_mock.mock()
    def test_fetch_uri(self, m):
        m.get("https://bad.uri", status_code=404)

        self.assertRaises(
            HTTPError, _uri.URIConfigurationSource, "https://bad.uri")

        m.get("https://good.uri", text="[DEFAULT]\nfoo=bar\n")
        source = _uri.URIConfigurationSource("https://good.uri")

        self.assertEqual(
            "bar", source.get("DEFAULT", "foo", cfg.StrOpt("foo"))[0])

    @base.mock.patch(
        "oslo_config.sources._uri.URIConfigurationSource._fetch_uri",
        side_effect=opts_to_ini)
    def test_configuration_source(self, mock_fetch_uri):
        group = "types"
        uri = make_uri(group)

        self.conf_fixture.load_raw_values(
            group=group,
            driver='remote_file',
            uri=uri
        )
        self.conf_fixture.config(config_source=[group])

        # testing driver loading
        self.assertEqual(self.conf._sources, [])
        self.conf._load_alternative_sources()
        self.assertEqual(type(self.conf._sources[0]),
                         _uri.URIConfigurationSource)

        source = self.conf._open_source_from_opt_group(group)

        self._register_opts(_extra_configs[uri]["data"])

        # non-existing option
        self.assertIs(sources._NoValue,
                      source.get("DEFAULT", "bar", cfg.StrOpt("bar"))[0])

        # 'g': group, 'o': option, 't': type, and 'v': value
        for g in _extra_configs[uri]["data"]:
            for o, (t, v) in _extra_configs[uri]["data"][g].items():
                self.assertEqual(str(v), str(source.get(g, o, t(o))[0]))
                self.assertEqual(v,
                                 self.conf[g][o] if g != "DEFAULT" else
                                 self.conf[o])

    @base.mock.patch(
        "oslo_config.sources._uri.URIConfigurationSource._fetch_uri",
        side_effect=opts_to_ini)
    def test_multiple_configuration_sources(self, mock_fetch_uri):
        groups = ["ini_1", "ini_2", "ini_3"]
        uri = make_uri("ini_3")

        for group in groups:
            self.conf_fixture.load_raw_values(
                group=group,
                driver='remote_file',
                uri=make_uri(group)
            )

        self.conf_fixture.config(config_source=groups)
        self.conf._load_alternative_sources()

        # ini_3 contains all options to be tested
        self._register_opts(_extra_configs[uri]["data"])

        # where options are 'abc', 'def', and 'ghi'
        # if the extra configs are loaded in the right order
        # the option name and option value will match correctly
        for option in _extra_configs[uri]["data"]["DEFAULT"]:
            self.assertEqual(option, self.conf[option])

    def test_list_opts(self):
        discovered_group = None
        for group in _list_opts.list_opts():
            if group[0] is not None:
                if group[0].name == "sample_remote_file_source":
                    discovered_group = group
                    break

        self.assertIsNotNone(discovered_group)

        self.assertEqual(
            _uri.URIConfigurationSourceDriver().list_options_for_discovery(),
            # NOTE: Ignore 'driver' option inserted automatically.
            discovered_group[1][1:],
        )
