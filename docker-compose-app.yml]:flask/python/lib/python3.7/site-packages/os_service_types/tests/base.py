# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
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

import copy
import datetime
import os
import tempfile

from oslotest import base

import os_service_types.service_types


class TestCase(base.BaseTestCase):
    """Base test case class before singleton protection is added."""

    def setUp(self):
        super(TestCase, self).setUp()

        self.builtin_content = os_service_types.service_types.BUILTIN_DATA
        self.builtin_version = self.builtin_content['version']

        # Set up copies of the data so that we can verify that we got the
        # copy of it we think we should.
        self.remote_version = datetime.datetime.utcnow().isoformat()
        self.remote_content = copy.deepcopy(self.builtin_content)
        self.remote_content['version'] = self.remote_version


class ServiceDataMixin(object):

    scenarios = [
        ('compute', dict(
            service_type='compute', official='compute', aliases=[],
            all_types=['compute'],
            api_reference='compute', api_reference_project=None,
            is_secondary=False, all_services=['compute'],
            is_known=True, is_alias=False, is_official=True, project='nova')),
        ('volumev2', dict(
            service_type='volumev2', official='block-storage', aliases=[],
            all_types=['block-storage', 'volumev3', 'volumev2', 'volume',
                       'block-store'],
            api_reference='block-storage', api_reference_project=None,
            is_known=True, is_alias=True, is_official=False,
            is_secondary=False, all_services=['block-storage'],
            project='cinder')),
        ('volumev3', dict(
            service_type='volumev3', official='block-storage', aliases=[],
            all_types=['block-storage', 'volumev3', 'volumev2', 'volume',
                       'block-store'],
            api_reference='block-storage', api_reference_project=None,
            is_known=True, is_alias=True, is_official=False,
            is_secondary=False, all_services=['block-storage'],
            project='cinder')),
        ('block-storage', dict(
            service_type='block-storage', official='block-storage',
            all_types=['block-storage', 'volumev3', 'volumev2', 'volume',
                       'block-store'],
            api_reference='block-storage', api_reference_project=None,
            aliases=['volumev3', 'volumev2', 'volume', 'block-store'],
            is_known=True, is_alias=False, is_official=True,
            is_secondary=False, all_services=['block-storage'],
            project='cinder')),
        ('block_storage', dict(
            service_type='block_storage', official='block-storage',
            all_types=['block-storage', 'volumev3', 'volumev2', 'volume',
                       'block-store'],
            api_reference='block-storage', api_reference_project=None,
            aliases=['volumev3', 'volumev2', 'volume', 'block-store'],
            is_known=True, is_alias=False, is_official=True,
            is_secondary=False, all_services=['block-storage'],
            project='cinder')),
        ('network', dict(
            service_type='network', official='network', aliases=[],
            all_types=['network'],
            api_reference='network', api_reference_project='neutron-lib',
            is_known=True, is_alias=False, is_official=True,
            is_secondary=False, all_services=['network'],
            project='neutron')),
        ('placement', dict(
            service_type='placement', official='placement', aliases=[],
            all_types=['placement'], all_services=['placement'],
            api_reference='placement', api_reference_project=None,
            is_known=True, is_alias=False, is_official=True,
            is_secondary=False, project='placement')),
        ('missing', dict(
            service_type='missing', official=None,
            aliases=[], all_services=[],
            all_types=['missing'],
            api_reference=None, api_reference_project=None,
            is_known=False, is_alias=False, is_official=False,
            is_secondary=False,
            project=None)),
    ]

    def test_get_service_type(self):
        if self.official:
            self.assertEqual(
                self.official,
                self.service_types.get_service_type(self.service_type))
        else:
            self.assertIsNone(
                self.service_types.get_service_type(self.service_type))

    def test_get_service_type_permissive(self):
        self.assertEqual(
            self.official or self.service_type,
            self.service_types.get_service_type(
                self.service_type, permissive=True))

    def test_get_aliases(self):
        self.assertEqual(
            self.aliases,
            self.service_types.get_aliases(self.service_type))

    def test_is_known(self):
        self.assertEqual(
            self.is_known,
            self.service_types.is_known(self.service_type))

    def test_is_alias(self):
        self.assertEqual(
            self.is_alias,
            self.service_types.is_alias(self.service_type))

    def test_is_official(self):
        self.assertEqual(
            self.is_official,
            self.service_types.is_official(self.service_type))

    def test_get_project_name(self):
        self.assertEqual(
            self.project,
            self.service_types.get_project_name(self.service_type))

    def test_get_service_data(self):
        service_data = self.service_types.get_service_data(self.service_type)
        # TODO(mordred) Once all the docs have been aligned, remove
        # self.api_reference and replace with self.service_type
        api_url = 'https://developer.openstack.org/api-ref/{api_reference}/'

        # Tests self.official here, since we expect to get data back for all
        # official projects, regardless of service_type being an alias or not
        if not self.official:
            self.assertIsNone(service_data)
        else:
            self.assertIsNotNone(service_data)
            self.assertEqual(self.project, service_data['project'])
            self.assertEqual(self.official, service_data['service_type'])
            self.assertEqual(
                api_url.format(api_reference=self.api_reference),
                service_data['api_reference'])

    def test_get_official_service_data(self):
        service_data = self.service_types.get_official_service_data(
            self.service_type)
        # TODO(mordred) Once all the docs have been aligned, remove
        # self.api_reference and replace with self.service_type
        api_url = 'https://developer.openstack.org/api-ref/{api_reference}/'

        # Tests self.is_official here, since we expect only get data back for
        # official projects.
        if not self.is_official:
            self.assertIsNone(service_data)
        else:
            self.assertIsNotNone(service_data)
            self.assertEqual(self.project, service_data['project'])
            self.assertEqual(self.official, service_data['service_type'])
            self.assertEqual(
                api_url.format(api_reference=self.api_reference),
                service_data['api_reference'])

    def test_empty_project_error(self):
        if not self.project:
            self.assertRaises(
                ValueError,
                self.service_types.get_service_data_for_project,
                self.project)

    def test_get_service_data_for_project(self):
        if self.is_secondary:
            self.skipTest("Secondary services have no project mapping")
            return
        elif not self.project:
            self.skipTest("Empty project is invalid but tested elsewhere.")
            return

        service_data = self.service_types.get_service_data_for_project(
            self.project)
        # TODO(mordred) Once all the docs have been aligned, remove
        # self.api_reference and replace with self.service_type
        api_url = 'https://developer.openstack.org/api-ref/{api_reference}/'

        self.assertIsNotNone(service_data)
        if self.api_reference_project:
            self.assertEqual(
                self.api_reference_project,
                service_data['api_reference_project'])
        else:
            self.assertEqual(self.project, service_data['project'])
        self.assertEqual(self.official, service_data['service_type'])
        self.assertEqual(
            api_url.format(api_reference=self.api_reference),
            service_data['api_reference'])

    def test_get_all_types(self):
        self.assertEqual(
            self.all_types,
            self.service_types.get_all_types(self.service_type))

    def test_all_get_service_data_for_project(self):
        if not self.project:
            self.skipTest("Empty project is invalid but tested elsewhere.")
            return

        all_data = self.service_types.get_all_service_data_for_project(
            self.project)
        for (index, data) in enumerate(all_data):
            self.assertEqual(
                data,
                self.service_types.get_service_data(self.all_services[index]))


class TemporaryFileMixin(base.BaseTestCase):

    def create_temp_file(self, mode='w', suffix='', prefix='tmp', dir=None,
                         text=False, delete=True):
        fd, name = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir,
                                    text=text)
        fd = os.fdopen(fd, mode)
        if delete:
            self.addCleanup(self._delete_temp, fd, name)
        return fd, name

    def _delete_temp(self, fd, name):
        fd.close()
        os.unlink(name)
