#    Copyright 2016 Mirantis, Inc.
#
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


from oslo_serialization import jsonutils
from oslo_serialization.serializer.base_serializer import BaseSerializer


class JSONSerializer(BaseSerializer):
    """JSON serializer based on the jsonutils module."""

    def __init__(self, default=jsonutils.to_primitive, encoding='utf-8'):
        self._default = default
        self._encoding = encoding

    def dump(self, obj, fp):
        return jsonutils.dump(obj, fp)

    def dump_as_bytes(self, obj):
        return jsonutils.dump_as_bytes(obj, default=self._default,
                                       encoding=self._encoding)

    def load(self, fp):
        return jsonutils.load(fp, encoding=self._encoding)

    def load_from_bytes(self, s):
        return jsonutils.loads(s, encoding=self._encoding)
