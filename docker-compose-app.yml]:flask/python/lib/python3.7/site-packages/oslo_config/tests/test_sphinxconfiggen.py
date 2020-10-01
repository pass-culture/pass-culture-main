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

from unittest import mock

from oslotest import base

from oslo_config import sphinxconfiggen


class SingleSampleGenerationTest(base.BaseTestCase):

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.isfile')
    @mock.patch('oslo_config.generator.main')
    def test_sample_gen_with_single_config_file(self, main, isfile, isdir):
        isfile.side_effect = [False, True]
        isdir.return_value = True

        config = mock.Mock(config_generator_config_file='nova-gen.conf',
                           sample_config_basename='nova')
        app = mock.Mock(srcdir='/opt/nova', config=config)
        sphinxconfiggen.generate_sample(app)

        main.assert_called_once_with(args=['--config-file',
                                           '/opt/nova/nova-gen.conf',
                                           '--output-file',
                                           '/opt/nova/nova.conf.sample'
                                           ])

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.isfile')
    @mock.patch('oslo_config.generator.main')
    def test_sample_gen_with_single_config_file_no_base(self, main, isfile,
                                                        isdir):
        isfile.side_effect = [False, True]
        isdir.return_value = True

        config = mock.Mock(config_generator_config_file='nova-gen.conf',
                           sample_config_basename=None)
        app = mock.Mock(srcdir='/opt/nova', config=config)
        sphinxconfiggen.generate_sample(app)

        main.assert_called_once_with(args=['--config-file',
                                           '/opt/nova/nova-gen.conf',
                                           '--output-file',
                                           '/opt/nova/sample.config'])


class MultipleSampleGenerationTest(base.BaseTestCase):

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.isfile')
    @mock.patch('oslo_config.generator.main')
    def test_multi_sample_gen(self, main, isfile, isdir):
        isfile.side_effect = [False, True, False, True]
        isdir.return_value = True

        multiple_configs = [('glance-api-gen.conf', 'glance-api'),
                            ('glance-reg-gen.conf', 'glance-reg')]
        config = mock.Mock(config_generator_config_file=multiple_configs)
        app = mock.Mock(srcdir='/opt/glance', config=config)
        sphinxconfiggen.generate_sample(app)

        self.assertEqual(main.call_count, 2)
        main.assert_any_call(args=['--config-file',
                                   '/opt/glance/glance-api-gen.conf',
                                   '--output-file',
                                   '/opt/glance/glance-api.conf.sample'])
        main.assert_any_call(args=['--config-file',
                                   '/opt/glance/glance-reg-gen.conf',
                                   '--output-file',
                                   '/opt/glance/glance-reg.conf.sample'])

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.isfile')
    @mock.patch('oslo_config.generator.main')
    def test_multi_sample_gen_with_without_one_base(self, main, isfile, isdir):
        isfile.side_effect = [False, True, False, True]
        isdir.return_value = True

        multiple_configs = [('glance-api-gen.conf', 'glance-api'),
                            ('glance-reg-gen.conf', None)]
        config = mock.Mock(config_generator_config_file=multiple_configs)
        app = mock.Mock(srcdir='/opt/glance', config=config)
        sphinxconfiggen.generate_sample(app)

        self.assertEqual(main.call_count, 2)
        main.assert_any_call(args=['--config-file',
                                   '/opt/glance/glance-api-gen.conf',
                                   '--output-file',
                                   '/opt/glance/glance-api.conf.sample'])
        main.assert_any_call(args=['--config-file',
                                   '/opt/glance/glance-reg-gen.conf',
                                   '--output-file',
                                   '/opt/glance/glance-reg-gen.conf.sample'])

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.isfile')
    @mock.patch('oslo_config.generator.main')
    def test_multi_sample_gen_with_without_any_base(self, main, isfile, isdir):
        isfile.side_effect = [False, True, False, True]
        isdir.return_value = True

        multiple_configs = [('glance-api-gen.conf', None),
                            ('glance-reg-gen.conf', None)]
        config = mock.Mock(config_generator_config_file=multiple_configs)
        app = mock.Mock(srcdir='/opt/glance', config=config)
        sphinxconfiggen.generate_sample(app)

        self.assertEqual(main.call_count, 2)
        main.assert_any_call(args=['--config-file',
                                   '/opt/glance/glance-api-gen.conf',
                                   '--output-file',
                                   '/opt/glance/glance-api-gen.conf.sample'])
        main.assert_any_call(args=['--config-file',
                                   '/opt/glance/glance-reg-gen.conf',
                                   '--output-file',
                                   '/opt/glance/glance-reg-gen.conf.sample'])
