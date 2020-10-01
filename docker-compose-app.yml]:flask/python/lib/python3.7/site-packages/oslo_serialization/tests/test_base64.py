# Copyright 2015 Red Hat
# All Rights Reserved.
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

from oslo_serialization import base64
from oslotest import base as test_base


class Base64Tests(test_base.BaseTestCase):

    def test_encode_as_bytes(self):
        self.assertEqual(b'dGV4dA==',
                         base64.encode_as_bytes(b'text'))
        self.assertEqual(b'dGV4dA==',
                         base64.encode_as_bytes(u'text'))
        self.assertEqual(b'ZTrDqQ==',
                         base64.encode_as_bytes(u'e:\xe9'))
        self.assertEqual(b'ZTrp',
                         base64.encode_as_bytes(u'e:\xe9', encoding='latin1'))

    def test_encode_as_text(self):
        self.assertEqual(u'dGV4dA==',
                         base64.encode_as_text(b'text'))
        self.assertEqual(u'dGV4dA==',
                         base64.encode_as_text(u'text'))
        self.assertEqual(u'ZTrDqQ==',
                         base64.encode_as_text(u'e:\xe9'))
        self.assertEqual(u'ZTrp',
                         base64.encode_as_text(u'e:\xe9', encoding='latin1'))

    def test_decode_as_bytes(self):
        self.assertEqual(b'text',
                         base64.decode_as_bytes(b'dGV4dA=='))
        self.assertEqual(b'text',
                         base64.decode_as_bytes(u'dGV4dA=='))

    def test_decode_as_bytes__error(self):
        self.assertRaises(TypeError,
                          base64.decode_as_bytes,
                          'hello world')

    def test_decode_as_text(self):
        self.assertEqual(u'text',
                         base64.decode_as_text(b'dGV4dA=='))
        self.assertEqual(u'text',
                         base64.decode_as_text(u'dGV4dA=='))
        self.assertEqual(u'e:\xe9',
                         base64.decode_as_text(u'ZTrDqQ=='))
        self.assertEqual(u'e:\xe9',
                         base64.decode_as_text(u'ZTrp', encoding='latin1'))
