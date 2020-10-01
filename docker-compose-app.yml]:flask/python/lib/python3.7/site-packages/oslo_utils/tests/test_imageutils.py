# Copyright (C) 2012 Yahoo! Inc.
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

from oslotest import base as test_base
import testscenarios

from oslo_utils import imageutils

load_tests = testscenarios.load_tests_apply_scenarios


class ImageUtilsRawTestCase(test_base.BaseTestCase):

    _image_name = [
        ('disk_config', dict(image_name='disk.config')),
    ]

    _file_format = [
        ('raw', dict(file_format='raw')),
    ]

    _virtual_size = [
        ('64M', dict(virtual_size='64M',
                     exp_virtual_size=67108864)),
        ('64M_with_byte_hint', dict(virtual_size='64M (67108844 bytes)',
                                    exp_virtual_size=67108844)),
        ('64M_byte', dict(virtual_size='67108844',
                          exp_virtual_size=67108844)),
        ('64_MiB_with_byte_hint', dict(virtual_size='64 MiB (67108844 bytes)',
                                       exp_virtual_size=67108844)),
        ('4.4M', dict(virtual_size='4.4M',
                      exp_virtual_size=4613735)),
        ('4.4M_with_byte_hint', dict(virtual_size='4.4M (4592640 bytes)',
                                     exp_virtual_size=4592640)),
        ('4.4_MiB_with_byte_hint', dict(virtual_size='4.4 MiB (4592640 bytes)',
                                        exp_virtual_size=4592640)),
        ('2K', dict(virtual_size='2K',
                    exp_virtual_size=2048)),
        ('2K_with_byte_hint', dict(virtual_size='2K (2048 bytes)',
                                   exp_virtual_size=2048)),
        ('2_KiB_with_byte_hint', dict(virtual_size='2 KiB (2048 bytes)',
                                      exp_virtual_size=2048)),
        ('1e+03_MiB', dict(virtual_size='1e+03 MiB',
                           exp_virtual_size=1048576000)),
    ]

    _disk_size = [
        ('96K', dict(disk_size='96K',
                     exp_disk_size=98304)),
        ('96_KiB', dict(disk_size='96 KiB',
                        exp_disk_size=98304)),
        ('96K_byte', dict(disk_size='98304',
                          exp_disk_size=98304)),
        ('98304_B', dict(disk_size='98304 B',
                         exp_disk_size=98304)),
        ('3.1G', dict(disk_size='3.1G',
                      exp_disk_size=3328599655)),
        ('3.1_GiB', dict(disk_size='3.1 GiB',
                         exp_disk_size=3328599655)),
        ('unavailable', dict(disk_size='unavailable',
                             exp_disk_size=0)),
        ('1e+03_MiB', dict(disk_size='1e+03 MiB',
                           exp_disk_size=1048576000)),
    ]

    _garbage_before_snapshot = [
        ('no_garbage', dict(garbage_before_snapshot=None)),
        ('garbage_before_snapshot_list', dict(garbage_before_snapshot=False)),
        ('garbage_after_snapshot_list', dict(garbage_before_snapshot=True)),
    ]

    _snapshot_count = [
        ('no_snapshots', dict(snapshot_count=None)),
        ('one_snapshots', dict(snapshot_count=1)),
        ('three_snapshots', dict(snapshot_count=3)),
    ]

    @classmethod
    def generate_scenarios(cls):
        cls.scenarios = testscenarios.multiply_scenarios(
            cls._image_name,
            cls._file_format,
            cls._virtual_size,
            cls._disk_size,
            cls._garbage_before_snapshot,
            cls._snapshot_count)

    def _initialize_img_info(self):
        return ('image: %s' % self.image_name,
                'file_format: %s' % self.file_format,
                'virtual_size: %s' % self.virtual_size,
                'disk_size: %s' % self.disk_size)

    def _insert_snapshots(self, img_info):
        img_info = img_info + ('Snapshot list:',)
        img_info = img_info + ('ID        '
                               'TAG                 '
                               'VM SIZE                '
                               'DATE       '
                               'VM CLOCK',)
        for i in range(self.snapshot_count):
            img_info = img_info + ('%d        '
                                   'd9a9784a500742a7bb95627bb3aace38    '
                                   '0 2012-08-20 10:52:46 '
                                   '00:00:00.000' % (i + 1),)
        return img_info

    def _base_validation(self, image_info):
        self.assertEqual(image_info.image, self.image_name)
        self.assertEqual(image_info.file_format, self.file_format)
        self.assertEqual(image_info.virtual_size, self.exp_virtual_size)
        self.assertEqual(image_info.disk_size, self.exp_disk_size)
        if self.snapshot_count is not None:
            self.assertEqual(len(image_info.snapshots), self.snapshot_count)

    def test_qemu_img_info(self):
        img_info = self._initialize_img_info()
        if self.garbage_before_snapshot is True:
            img_info = img_info + ('blah BLAH: bb',)
        if self.snapshot_count is not None:
            img_info = self._insert_snapshots(img_info)
        if self.garbage_before_snapshot is False:
            img_info = img_info + ('junk stuff: bbb',)
        example_output = '\n'.join(img_info)
        image_info = imageutils.QemuImgInfo(example_output)
        self._base_validation(image_info)


ImageUtilsRawTestCase.generate_scenarios()


class ImageUtilsQemuTestCase(ImageUtilsRawTestCase):

    _file_format = [
        ('qcow2', dict(file_format='qcow2')),
    ]

    _qcow2_cluster_size = [
        ('65536', dict(cluster_size='65536', exp_cluster_size=65536)),
    ]

    _qcow2_encrypted = [
        ('no_encryption', dict(encrypted=None)),
        ('encrypted', dict(encrypted='yes')),
    ]

    _qcow2_backing_file = [
        ('no_backing_file', dict(backing_file=None)),
        ('backing_file_path',
         dict(backing_file='/var/lib/nova/a328c7998805951a_2',
              exp_backing_file='/var/lib/nova/a328c7998805951a_2')),
        ('backing_file_path_with_actual_path',
         dict(backing_file='/var/lib/nova/a328c7998805951a_2 '
                           '(actual path: /b/3a988059e51a_2)',
              exp_backing_file='/b/3a988059e51a_2')),
    ]

    @classmethod
    def generate_scenarios(cls):
        cls.scenarios = testscenarios.multiply_scenarios(
            cls._image_name,
            cls._file_format,
            cls._virtual_size,
            cls._disk_size,
            cls._garbage_before_snapshot,
            cls._snapshot_count,
            cls._qcow2_cluster_size,
            cls._qcow2_encrypted,
            cls._qcow2_backing_file)

    def test_qemu_img_info(self):
        img_info = self._initialize_img_info()
        img_info = img_info + ('cluster_size: %s' % self.cluster_size,)
        if self.backing_file is not None:
            img_info = img_info + ('backing file: %s' %
                                   self.backing_file,)
        if self.encrypted is not None:
            img_info = img_info + ('encrypted: %s' % self.encrypted,)
        if self.garbage_before_snapshot is True:
            img_info = img_info + ('blah BLAH: bb',)
        if self.snapshot_count is not None:
            img_info = self._insert_snapshots(img_info)
        if self.garbage_before_snapshot is False:
            img_info = img_info + ('junk stuff: bbb',)
        example_output = '\n'.join(img_info)
        image_info = imageutils.QemuImgInfo(example_output)
        self._base_validation(image_info)
        self.assertEqual(image_info.cluster_size, self.exp_cluster_size)
        if self.backing_file is not None:
            self.assertEqual(image_info.backing_file,
                             self.exp_backing_file)
        if self.encrypted is not None:
            self.assertEqual(image_info.encrypted, self.encrypted)


ImageUtilsQemuTestCase.generate_scenarios()


class ImageUtilsBlankTestCase(test_base.BaseTestCase):
    def test_qemu_img_info_blank(self):
        example_output = '\n'.join(['image: None', 'file_format: None',
                                    'virtual_size: None', 'disk_size: None',
                                    'cluster_size: None',
                                    'backing_file: None'])
        image_info = imageutils.QemuImgInfo()
        self.assertEqual(str(image_info), example_output)
        self.assertEqual(len(image_info.snapshots), 0)


class ImageUtilsJSONTestCase(test_base.BaseTestCase):
    def test_qemu_img_info_json_format(self):
        img_output = '''{
                       "virtual-size": 41126400,
                       "filename": "fake_img",
                       "cluster-size": 65536,
                       "format": "qcow2",
                       "actual-size": 13168640,
                       "format-specific": {"data": {"foo": "bar"}}
                      }'''
        image_info = imageutils.QemuImgInfo(img_output, format='json')
        self.assertEqual(41126400, image_info.virtual_size)
        self.assertEqual('fake_img', image_info.image)
        self.assertEqual(65536, image_info.cluster_size)
        self.assertEqual('qcow2', image_info.file_format)
        self.assertEqual(13168640, image_info.disk_size)
        self.assertEqual("bar", image_info.format_specific["data"]["foo"])

    def test_qemu_img_info_json_format_blank(self):
        img_output = '{}'
        image_info = imageutils.QemuImgInfo(img_output, format='json')
        self.assertIsNone(image_info.virtual_size)
        self.assertIsNone(image_info.image)
        self.assertIsNone(image_info.cluster_size)
        self.assertIsNone(image_info.file_format)
        self.assertIsNone(image_info.disk_size)
        self.assertIsNone(image_info.format_specific)
