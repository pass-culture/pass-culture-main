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

from lxml import etree

from keystoneauth1 import session
from keystoneauth1.tests.unit import utils

ROOTDIR = os.path.dirname(os.path.abspath(__file__))
XMLDIR = os.path.join(ROOTDIR, 'examples', 'xml/')


def make_oneline(s):
    return etree.tostring(etree.XML(s)).replace(b'\n', b'')


def _load_xml(filename):
    with open(XMLDIR + filename, 'rb') as f:
        return f.read()


class TestCase(utils.TestCase):

    TEST_URL = 'https://keystone:5000/v3'

    def setUp(self):
        super(TestCase, self).setUp()
        self.session = session.Session()
