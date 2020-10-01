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

import stevedore

from keystoneauth1 import loading
from keystoneauth1.tests.unit.loading import utils


class EntryPointTests(utils.TestCase):
    """Simple test that will check that all entry points are loadable."""

    def test_all_entry_points_are_valid(self):
        errors = []

        def raise_exception_callback(manager, entrypoint, exc):
            error = ("Cannot load '%(entrypoint)s' entry_point: %(error)s'" %
                     {"entrypoint": entrypoint, "error": exc})
            errors.append(error)

        stevedore.ExtensionManager(
            namespace=loading.PLUGIN_NAMESPACE,
            on_load_failure_callback=raise_exception_callback
        )

        self.assertEqual([], errors)
