# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
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

from sphinx.util import logging

from oslo_config import generator

LOG = logging.getLogger(__name__)


def generate_sample(app):

    if not app.config.config_generator_config_file:
        LOG.warning("No config_generator_config_file is specified, "
                    "skipping sample config generation")
        return

    # Decided to update the existing config option
    # config_generator_config_file to support a value that is a list of
    # tuples, containing the file names as (input, output).
    # We need to retain support for the option referring to a single string,
    # and using the sample_config_basename for the output file in that case.
    # After we release support for both forms of the option, we can update
    # projects to always use the list of tuples, then remove
    # sample_config_basename and the support for config_generator_config_file
    # being a single string.

    if isinstance(app.config.config_generator_config_file, list):
        for config_file, base_name in app.config.config_generator_config_file:
            if base_name is None:
                base_name = _get_default_basename(config_file)
            _generate_sample(app, config_file, base_name)
    else:
        _generate_sample(app,
                         app.config.config_generator_config_file,
                         app.config.sample_config_basename)


def _get_default_basename(config_file):
    return os.path.splitext(os.path.basename(config_file))[0]


def _generate_sample(app, config_file, base_name):

    def info(msg):
        LOG.info('[%s] %s' % (__name__, msg))

    # If we are given a file that isn't an absolute path, look for it
    # in the source directory if it doesn't exist.
    candidates = [
        config_file,
        os.path.join(app.srcdir, config_file,),
    ]
    for c in candidates:
        if os.path.isfile(c):
            info('reading config generator instructions from %s' % c)
            config_path = c
            break
    else:
        raise ValueError(
            "Could not find config_generator_config_file %r" %
            app.config.config_generator_config_file)

    if base_name:
        out_file = os.path.join(app.srcdir, base_name) + '.conf.sample'
        if not os.path.isdir(os.path.dirname(os.path.abspath(out_file))):
            os.mkdir(os.path.dirname(os.path.abspath(out_file)))
    else:
        file_name = 'sample.config'
        out_file = os.path.join(app.srcdir, file_name)

    info('writing sample configuration to %s' % out_file)
    generator.main(args=['--config-file', config_path,
                         '--output-file', out_file])


def setup(app):
    app.add_config_value('config_generator_config_file', None, 'env')
    app.add_config_value('sample_config_basename', None, 'env')
    app.connect('builder-inited', generate_sample)
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
