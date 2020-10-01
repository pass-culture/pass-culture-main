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

from keystoneauth1.extras.oauth1 import v3
from keystoneauth1 import loading


# NOTE(jamielennox): This is not a BaseV3Loader because we don't want to
# include the scoping options like project-id in the option list
class V3OAuth1(loading.BaseIdentityLoader):

    @property
    def plugin_class(self):
        return v3.OAuth1

    @property
    def available(self):
        return v3.oauth1 is not None

    def get_options(self):
        options = super(V3OAuth1, self).get_options()

        options.extend([
            loading.Opt('consumer-key',
                        required=True,
                        help='OAuth Consumer ID/Key'),
            loading.Opt('consumer-secret',
                        required=True,
                        help='OAuth Consumer Secret'),
            loading.Opt('access-key',
                        required=True,
                        help='OAuth Access Key'),
            loading.Opt('access-secret',
                        required=True,
                        help='OAuth Access Secret'),
        ])

        return options
