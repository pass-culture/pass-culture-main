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

from keystoneauth1 import exceptions
from keystoneauth1.tests.unit import utils


class ExceptionTests(utils.TestCase):

    def test_clientexception_with_message(self):
        test_message = 'Unittest exception message.'
        exc = exceptions.ClientException(message=test_message)
        self.assertEqual(test_message, exc.message)

    def test_clientexception_with_no_message(self):
        exc = exceptions.ClientException()
        self.assertEqual(exceptions.ClientException.__name__,
                         exc.message)

    def test_using_default_message(self):
        exc = exceptions.AuthorizationFailure()
        self.assertEqual(exceptions.AuthorizationFailure.message,
                         exc.message)
