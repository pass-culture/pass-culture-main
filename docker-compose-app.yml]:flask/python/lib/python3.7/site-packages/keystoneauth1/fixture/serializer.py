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

"""A serializer to emit YAML but with request body in nicely formatted JSON."""

import json
import os

import betamax.serializers.base
import six
import yaml


def _should_use_block(value):
    for c in u"\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
        if c in value:
            return True
    return False


def _represent_scalar(self, tag, value, style=None):
    if style is None:
        if _should_use_block(value):
            style = '|'
        else:
            style = self.default_style

    node = yaml.representer.ScalarNode(tag, value, style=style)
    if self.alias_key is not None:
        self.represented_objects[self.alias_key] = node
    return node


def _unicode_representer(dumper, uni):
    node = yaml.ScalarNode(tag=u'tag:yaml.org,2002:str', value=uni)
    return node


def _indent_json(val):
    if not val:
        return ''

    return json.dumps(
        json.loads(val), indent=2,
        separators=(',', ': '), sort_keys=False,
        default=six.text_type)


def _is_json_body(interaction):
    content_type = interaction['headers'].get('Content-Type', [])
    return 'application/json' in content_type


class YamlJsonSerializer(betamax.serializers.base.BaseSerializer):

    name = "yamljson"

    @staticmethod
    def generate_cassette_name(cassette_library_dir, cassette_name):
        return os.path.join(
            cassette_library_dir, "{name}.yaml".format(name=cassette_name))

    def serialize(self, cassette_data):
        # Reserialize internal json with indentation
        for interaction in cassette_data['http_interactions']:
            for key in ('request', 'response'):
                if _is_json_body(interaction[key]):
                    interaction[key]['body']['string'] = _indent_json(
                        interaction[key]['body']['string'])

        class MyDumper(yaml.Dumper):
            """Specialized Dumper which does nice blocks and unicode."""

        yaml.representer.BaseRepresenter.represent_scalar = _represent_scalar

        MyDumper.add_representer(six.text_type, _unicode_representer)

        return yaml.dump(
            cassette_data, Dumper=MyDumper, default_flow_style=False)

    def deserialize(self, cassette_data):
        try:
            deserialized = yaml.safe_load(cassette_data)
        except yaml.error.YAMLError:
            deserialized = None

        if deserialized is not None:
            return deserialized
        return {}
