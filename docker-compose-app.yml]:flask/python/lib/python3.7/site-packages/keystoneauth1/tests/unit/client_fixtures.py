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

from keystoneauth1 import fixture as kfixture


def project_scoped_token():
    fixture = kfixture.V3Token(
        user_id='c4da488862bd435c9e6c0275a0d0e49a',
        user_name='exampleuser',
        user_domain_id='4e6893b7ba0b4006840c3845660b86ed',
        user_domain_name='exampledomain',
        expires='2010-11-01T03:32:15-05:00',
        project_id='225da22d3ce34b15877ea70b2a575f58',
        project_name='exampleproject',
        project_domain_id='4e6893b7ba0b4006840c3845660b86ed',
        project_domain_name='exampledomain')

    fixture.add_role(id='76e72a', name='admin')
    fixture.add_role(id='f4f392', name='member')

    region = 'RegionOne'
    tenant = '225da22d3ce34b15877ea70b2a575f58'

    service = fixture.add_service('volume')
    service.add_standard_endpoints(
        public='http://public.com:8776/v1/%s' % tenant,
        internal='http://internal:8776/v1/%s' % tenant,
        admin='http://admin:8776/v1/%s' % tenant,
        region=region)

    service = fixture.add_service('image')
    service.add_standard_endpoints(public='http://public.com:9292/v1',
                                   internal='http://internal:9292/v1',
                                   admin='http://admin:9292/v1',
                                   region=region)

    service = fixture.add_service('compute')
    service.add_standard_endpoints(
        public='http://public.com:8774/v2/%s' % tenant,
        internal='http://internal:8774/v2/%s' % tenant,
        admin='http://admin:8774/v2/%s' % tenant,
        region=region)

    service = fixture.add_service('ec2')
    service.add_standard_endpoints(
        public='http://public.com:8773/services/Cloud',
        internal='http://internal:8773/services/Cloud',
        admin='http://admin:8773/services/Admin',
        region=region)

    service = fixture.add_service('identity')
    service.add_standard_endpoints(public='http://public.com:5000/v3',
                                   internal='http://internal:5000/v3',
                                   admin='http://admin:35357/v3',
                                   region=region)

    return fixture


def domain_scoped_token():
    fixture = kfixture.V3Token(
        user_id='c4da488862bd435c9e6c0275a0d0e49a',
        user_name='exampleuser',
        user_domain_id='4e6893b7ba0b4006840c3845660b86ed',
        user_domain_name='exampledomain',
        expires='2010-11-01T03:32:15-05:00',
        domain_id='8e9283b7ba0b1038840c3842058b86ab',
        domain_name='anotherdomain')

    fixture.add_role(id='76e72a', name='admin')
    fixture.add_role(id='f4f392', name='member')
    region = 'RegionOne'

    service = fixture.add_service('volume')
    service.add_standard_endpoints(public='http://public.com:8776/v1/None',
                                   internal='http://internal.com:8776/v1/None',
                                   admin='http://admin.com:8776/v1/None',
                                   region=region)

    service = fixture.add_service('image')
    service.add_standard_endpoints(public='http://public.com:9292/v1',
                                   internal='http://internal:9292/v1',
                                   admin='http://admin:9292/v1',
                                   region=region)

    service = fixture.add_service('compute')
    service.add_standard_endpoints(public='http://public.com:8774/v1.1/None',
                                   internal='http://internal:8774/v1.1/None',
                                   admin='http://admin:8774/v1.1/None',
                                   region=region)

    service = fixture.add_service('ec2')
    service.add_standard_endpoints(
        public='http://public.com:8773/services/Cloud',
        internal='http://internal:8773/services/Cloud',
        admin='http://admin:8773/services/Admin',
        region=region)

    service = fixture.add_service('identity')
    service.add_standard_endpoints(public='http://public.com:5000/v3',
                                   internal='http://internal:5000/v3',
                                   admin='http://admin:35357/v3',
                                   region=region)

    return fixture


AUTH_SUBJECT_TOKEN = '3e2813b7ba0b4006840c3825860b86ed'

AUTH_RESPONSE_HEADERS = {
    'X-Subject-Token': AUTH_SUBJECT_TOKEN,
}
