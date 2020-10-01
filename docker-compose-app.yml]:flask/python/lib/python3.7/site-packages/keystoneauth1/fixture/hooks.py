# Copyright (c) 2016 Hewlett-Packard Enterprise Development Company, L.P.
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
"""Custom hooks for betamax and keystoneauth.

   Module providing a set of hooks specially designed for
   interacting with clouds and keystone authentication.

:author: Yolanda Robla
"""

import json


def mask_fixture_values(nested, prev_key):
    for key, value in nested.items():
        if isinstance(value, dict):
            mask_fixture_values(value, key)
        else:
            if key in ('tenantName', 'username'):
                nested[key] = 'dummy'
            elif prev_key in ('user', 'project', 'tenant') and key == 'name':
                nested[key] = 'dummy'
            elif prev_key == 'domain' and key == 'id':
                nested[key] = 'dummy'
            elif key == 'password':
                nested[key] = '********'
            elif prev_key == 'token' and key in ('expires', 'expires_at'):
                nested[key] = '9999-12-31T23:59:59Z'


def pre_record_hook(interaction, cassette):
    """Hook to mask saved data.

    This hook will be triggered before saving the interaction, and
    will perform two tasks:
    - mask user, project and password in the saved data
    - set token expiration time to an inifinite time.
    """
    request_body = interaction.data['request']['body']
    if request_body.get('string'):
        parsed_content = json.loads(request_body['string'])
        mask_fixture_values(parsed_content, None)
        request_body['string'] = json.dumps(parsed_content)

    response_body = interaction.data['response']['body']
    if response_body.get('string'):
        parsed_content = json.loads(response_body['string'])
        mask_fixture_values(parsed_content, None)
        response_body['string'] = json.dumps(parsed_content)
