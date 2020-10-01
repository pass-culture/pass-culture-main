# -*- coding: utf-8 -*-

# Copyright 2011 OpenStack Foundation.
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

import collections
import copy
import math
from unittest import mock

import ddt
from oslotest import base as test_base
import six
import testscenarios

from oslo_utils import strutils
from oslo_utils import units

load_tests = testscenarios.load_tests_apply_scenarios


class StrUtilsTest(test_base.BaseTestCase):

    @mock.patch("six.text_type")
    def test_bool_bool_from_string_no_text(self, mock_text):
        self.assertTrue(strutils.bool_from_string(True))
        self.assertFalse(strutils.bool_from_string(False))
        self.assertEqual(0, mock_text.call_count)

    def test_bool_bool_from_string(self):
        self.assertTrue(strutils.bool_from_string(True))
        self.assertFalse(strutils.bool_from_string(False))

    def test_bool_bool_from_string_default(self):
        self.assertTrue(strutils.bool_from_string('', default=True))
        self.assertFalse(strutils.bool_from_string('wibble', default=False))

    def _test_bool_from_string(self, c):
        self.assertTrue(strutils.bool_from_string(c('true')))
        self.assertTrue(strutils.bool_from_string(c('TRUE')))
        self.assertTrue(strutils.bool_from_string(c('on')))
        self.assertTrue(strutils.bool_from_string(c('On')))
        self.assertTrue(strutils.bool_from_string(c('yes')))
        self.assertTrue(strutils.bool_from_string(c('YES')))
        self.assertTrue(strutils.bool_from_string(c('yEs')))
        self.assertTrue(strutils.bool_from_string(c('1')))
        self.assertTrue(strutils.bool_from_string(c('T')))
        self.assertTrue(strutils.bool_from_string(c('t')))
        self.assertTrue(strutils.bool_from_string(c('Y')))
        self.assertTrue(strutils.bool_from_string(c('y')))

        self.assertFalse(strutils.bool_from_string(c('false')))
        self.assertFalse(strutils.bool_from_string(c('FALSE')))
        self.assertFalse(strutils.bool_from_string(c('off')))
        self.assertFalse(strutils.bool_from_string(c('OFF')))
        self.assertFalse(strutils.bool_from_string(c('no')))
        self.assertFalse(strutils.bool_from_string(c('0')))
        self.assertFalse(strutils.bool_from_string(c('42')))
        self.assertFalse(strutils.bool_from_string(c(
                         'This should not be True')))
        self.assertFalse(strutils.bool_from_string(c('F')))
        self.assertFalse(strutils.bool_from_string(c('f')))
        self.assertFalse(strutils.bool_from_string(c('N')))
        self.assertFalse(strutils.bool_from_string(c('n')))

        # Whitespace should be stripped
        self.assertTrue(strutils.bool_from_string(c(' 1 ')))
        self.assertTrue(strutils.bool_from_string(c(' true ')))
        self.assertFalse(strutils.bool_from_string(c(' 0 ')))
        self.assertFalse(strutils.bool_from_string(c(' false ')))

    def test_bool_from_string(self):
        self._test_bool_from_string(lambda s: s)

    def test_unicode_bool_from_string(self):
        self._test_bool_from_string(six.text_type)
        self.assertFalse(strutils.bool_from_string(u'使用', strict=False))

        exc = self.assertRaises(ValueError, strutils.bool_from_string,
                                u'使用', strict=True)
        expected_msg = (u"Unrecognized value '使用', acceptable values are:"
                        u" '0', '1', 'f', 'false', 'n', 'no', 'off', 'on',"
                        u" 't', 'true', 'y', 'yes'")
        self.assertEqual(expected_msg, six.text_type(exc))

    def test_other_bool_from_string(self):
        self.assertFalse(strutils.bool_from_string(None))
        self.assertFalse(strutils.bool_from_string(mock.Mock()))

    def test_int_bool_from_string(self):
        self.assertTrue(strutils.bool_from_string(1))

        self.assertFalse(strutils.bool_from_string(-1))
        self.assertFalse(strutils.bool_from_string(0))
        self.assertFalse(strutils.bool_from_string(2))

    def test_strict_bool_from_string(self):
        # None isn't allowed in strict mode
        exc = self.assertRaises(ValueError, strutils.bool_from_string, None,
                                strict=True)
        expected_msg = ("Unrecognized value 'None', acceptable values are:"
                        " '0', '1', 'f', 'false', 'n', 'no', 'off', 'on',"
                        " 't', 'true', 'y', 'yes'")
        self.assertEqual(expected_msg, str(exc))

        # Unrecognized strings aren't allowed
        self.assertFalse(strutils.bool_from_string('Other', strict=False))
        exc = self.assertRaises(ValueError, strutils.bool_from_string, 'Other',
                                strict=True)
        expected_msg = ("Unrecognized value 'Other', acceptable values are:"
                        " '0', '1', 'f', 'false', 'n', 'no', 'off', 'on',"
                        " 't', 'true', 'y', 'yes'")
        self.assertEqual(expected_msg, str(exc))

        # Unrecognized numbers aren't allowed
        exc = self.assertRaises(ValueError, strutils.bool_from_string, 2,
                                strict=True)
        expected_msg = ("Unrecognized value '2', acceptable values are:"
                        " '0', '1', 'f', 'false', 'n', 'no', 'off', 'on',"
                        " 't', 'true', 'y', 'yes'")
        self.assertEqual(expected_msg, str(exc))

        # False-like values are allowed
        self.assertFalse(strutils.bool_from_string('f', strict=True))
        self.assertFalse(strutils.bool_from_string('false', strict=True))
        self.assertFalse(strutils.bool_from_string('off', strict=True))
        self.assertFalse(strutils.bool_from_string('n', strict=True))
        self.assertFalse(strutils.bool_from_string('no', strict=True))
        self.assertFalse(strutils.bool_from_string('0', strict=True))

        self.assertTrue(strutils.bool_from_string('1', strict=True))

        # Avoid font-similarity issues (one looks like lowercase-el, zero like
        # oh, etc...)
        for char in ('O', 'o', 'L', 'l', 'I', 'i'):
            self.assertRaises(ValueError, strutils.bool_from_string, char,
                              strict=True)

    def test_int_from_bool_as_string(self):
        self.assertEqual(1, strutils.int_from_bool_as_string(True))
        self.assertEqual(0, strutils.int_from_bool_as_string(False))

    def test_is_valid_boolstr(self):
        self.assertTrue(strutils.is_valid_boolstr('true'))
        self.assertTrue(strutils.is_valid_boolstr('false'))
        self.assertTrue(strutils.is_valid_boolstr('yes'))
        self.assertTrue(strutils.is_valid_boolstr('no'))
        self.assertTrue(strutils.is_valid_boolstr('y'))
        self.assertTrue(strutils.is_valid_boolstr('n'))
        self.assertTrue(strutils.is_valid_boolstr('1'))
        self.assertTrue(strutils.is_valid_boolstr('0'))
        self.assertTrue(strutils.is_valid_boolstr(1))
        self.assertTrue(strutils.is_valid_boolstr(0))

        self.assertFalse(strutils.is_valid_boolstr('maybe'))
        self.assertFalse(strutils.is_valid_boolstr('only on tuesdays'))

    def test_slugify(self):
        to_slug = strutils.to_slug
        self.assertRaises(TypeError, to_slug, True)
        self.assertEqual(six.u("hello"), to_slug("hello"))
        self.assertEqual(six.u("two-words"), to_slug("Two Words"))
        self.assertEqual(six.u("ma-any-spa-ce-es"),
                         to_slug("Ma-any\t spa--ce- es"))
        self.assertEqual(six.u("excamation"), to_slug("exc!amation!"))
        self.assertEqual(six.u("ampserand"), to_slug("&ampser$and"))
        self.assertEqual(six.u("ju5tnum8er"), to_slug("ju5tnum8er"))
        self.assertEqual(six.u("strip-"), to_slug(" strip - "))
        self.assertEqual(six.u("perche"), to_slug(six.b("perch\xc3\xa9")))
        self.assertEqual(six.u("strange"),
                         to_slug("\x80strange", errors="ignore"))


class StringToBytesTest(test_base.BaseTestCase):

    _unit_system = [
        ('si', dict(unit_system='SI')),
        ('iec', dict(unit_system='IEC')),
        ('mixed', dict(unit_system='mixed')),
        ('invalid_unit_system', dict(unit_system='KKK', assert_error=True)),
    ]

    _sign = [
        ('no_sign', dict(sign='')),
        ('positive', dict(sign='+')),
        ('negative', dict(sign='-')),
        ('invalid_sign', dict(sign='~', assert_error=True)),
    ]

    _magnitude = [
        ('integer', dict(magnitude='79')),
        ('decimal', dict(magnitude='7.9')),
        ('decimal_point_start', dict(magnitude='.9')),
        ('decimal_point_end', dict(magnitude='79.', assert_error=True)),
        ('invalid_literal', dict(magnitude='7.9.9', assert_error=True)),
        ('garbage_value', dict(magnitude='asdf', assert_error=True)),
    ]

    _unit_prefix = [
        ('no_unit_prefix', dict(unit_prefix='')),
        ('k', dict(unit_prefix='k')),
        ('K', dict(unit_prefix='K')),
        ('M', dict(unit_prefix='M')),
        ('G', dict(unit_prefix='G')),
        ('T', dict(unit_prefix='T')),
        ('Ki', dict(unit_prefix='Ki')),
        ('Mi', dict(unit_prefix='Mi')),
        ('Gi', dict(unit_prefix='Gi')),
        ('Ti', dict(unit_prefix='Ti')),
        ('invalid_unit_prefix', dict(unit_prefix='B', assert_error=True)),
    ]

    _unit_suffix = [
        ('b', dict(unit_suffix='b')),
        ('bit', dict(unit_suffix='bit')),
        ('B', dict(unit_suffix='B')),
        ('invalid_unit_suffix', dict(unit_suffix='Kg', assert_error=True)),
    ]

    _return_int = [
        ('return_dec', dict(return_int=False)),
        ('return_int', dict(return_int=True)),
    ]

    @classmethod
    def generate_scenarios(cls):
        cls.scenarios = testscenarios.multiply_scenarios(cls._unit_system,
                                                         cls._sign,
                                                         cls._magnitude,
                                                         cls._unit_prefix,
                                                         cls._unit_suffix,
                                                         cls._return_int)

    def test_string_to_bytes(self):

        def _get_quantity(sign, magnitude, unit_suffix):
            res = float('%s%s' % (sign, magnitude))
            if unit_suffix in ['b', 'bit']:
                res /= 8
            return res

        def _get_constant(unit_prefix, unit_system):
            if not unit_prefix:
                return 1
            elif unit_system == 'SI':
                res = getattr(units, unit_prefix)
            elif unit_system == 'IEC':
                if unit_prefix.endswith('i'):
                    res = getattr(units, unit_prefix)
                else:
                    res = getattr(units, '%si' % unit_prefix)
            elif unit_system == 'mixed':
                # Note: this will return 'i' units as power-of-two,
                # and other units as power-of-ten.  Additionally, for
                # compatability a "K" is interpreted as "k" in mixed
                # mode
                if unit_prefix == 'K':
                    unit_prefix = 'k'
                res = getattr(units, unit_prefix)
            return res

        text = ''.join([self.sign, self.magnitude, self.unit_prefix,
                        self.unit_suffix])
        err_si = self.unit_system == 'SI' and (self.unit_prefix == 'K' or
                                               self.unit_prefix.endswith('i'))
        err_iec = self.unit_system == 'IEC' and self.unit_prefix == 'k'
        if getattr(self, 'assert_error', False) or err_si or err_iec:
            self.assertRaises(ValueError, strutils.string_to_bytes,
                              text, unit_system=self.unit_system,
                              return_int=self.return_int)
            return
        quantity = _get_quantity(self.sign, self.magnitude, self.unit_suffix)
        constant = _get_constant(self.unit_prefix, self.unit_system)
        expected = quantity * constant
        actual = strutils.string_to_bytes(text, unit_system=self.unit_system,
                                          return_int=self.return_int)
        if self.return_int:
            self.assertEqual(actual, int(math.ceil(expected)))
        else:
            self.assertAlmostEqual(actual, expected)


StringToBytesTest.generate_scenarios()


class MaskPasswordTestCase(test_base.BaseTestCase):

    def test_sanitize_keys(self):

        lowered = [k.lower() for k in strutils._SANITIZE_KEYS]
        message = "The _SANITIZE_KEYS must all be lowercase."
        self.assertEqual(strutils._SANITIZE_KEYS, lowered, message)

    def test_json(self):
        # Test 'adminPass' w/o spaces
        payload = """{'adminPass':'TL0EfN33'}"""
        expected = """{'adminPass':'***'}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'adminPass' with spaces
        payload = """{ 'adminPass' : 'TL0EfN33' }"""
        expected = """{ 'adminPass' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_pass' w/o spaces
        payload = """{'admin_pass':'TL0EfN33'}"""
        expected = """{'admin_pass':'***'}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_pass' with spaces
        payload = """{ 'admin_pass' : 'TL0EfN33' }"""
        expected = """{ 'admin_pass' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_password' w/o spaces
        payload = """{'admin_password':'TL0EfN33'}"""
        expected = """{'admin_password':'***'}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_password' with spaces
        payload = """{ 'admin_password' : 'TL0EfN33' }"""
        expected = """{ 'admin_password' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'password' w/o spaces
        payload = """{'password':'TL0EfN33'}"""
        expected = """{'password':'***'}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'password' with spaces
        payload = """{ 'password' : 'TL0EfN33' }"""
        expected = """{ 'password' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'auth_password' w/o spaces
        payload = """{'auth_password':'TL0EfN33'}"""
        expected = """{'auth_password':'***'}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'auth_password' with spaces
        payload = """{ 'auth_password' : 'TL0EfN33' }"""
        expected = """{ 'auth_password' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'secret_uuid' w/o spaces
        payload = """{'secret_uuid':'myuuid'}"""
        expected = """{'secret_uuid':'***'}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'secret_uuid' with spaces
        payload = """{ 'secret_uuid' : 'myuuid' }"""
        expected = """{ 'secret_uuid' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'token' w/o spaces
        payload = """{'token':'token'}"""
        expected = """{'token':'***'}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'token' with spaces
        payload = """{ 'token' : 'token' }"""
        expected = """{ 'token' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'fernetkey'
        payload = """{ 'fernetkey' : 'token' }"""
        expected = """{ 'fernetkey' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'FernetKey'
        payload = """{ 'FernetKey' : 'token' }"""
        expected = """{ 'FernetKey' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'sslkey'
        payload = """{ 'sslkey' : 'token' }"""
        expected = """{ 'sslkey' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'SslKey'
        payload = """{ 'SslKey' : 'token' }"""
        expected = """{ 'SslKey' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'passphrase'
        payload = """{ 'passphrase' : 'token' }"""
        expected = """{ 'passphrase' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'PassPhrase'
        payload = """{ 'PassPhrase' : 'token' }"""
        expected = """{ 'PassPhrase' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Some real-life cases
        # Test 'KeystoneFernetKey1'
        payload = """{ 'KeystoneFernetKey1' : 'token' }"""
        expected = """{ 'KeystoneFernetKey1' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'OctaviaCaKeyPassword'
        payload = """{ 'OctaviaCaKeyPassword' : 'token' }"""
        expected = """{ 'OctaviaCaKeyPassword' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'OctaviaCaKeyPassphrase'
        payload = """{ 'OctaviaCaKeyPassphrase' : 'token' }"""
        expected = """{ 'OctaviaCaKeyPassphrase' : '***' }"""
        self.assertEqual(expected, strutils.mask_password(payload))

    def test_xml(self):
        # Test 'adminPass' w/o spaces
        payload = """<adminPass>TL0EfN33</adminPass>"""
        expected = """<adminPass>***</adminPass>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'adminPass' with spaces
        payload = """<adminPass>
                        TL0EfN33
                     </adminPass>"""
        expected = """<adminPass>***</adminPass>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_pass' w/o spaces
        payload = """<admin_pass>TL0EfN33</admin_pass>"""
        expected = """<admin_pass>***</admin_pass>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_pass' with spaces
        payload = """<admin_pass>
                        TL0EfN33
                     </admin_pass>"""
        expected = """<admin_pass>***</admin_pass>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_password' w/o spaces
        payload = """<admin_password>TL0EfN33</admin_password>"""
        expected = """<admin_password>***</admin_password>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_password' with spaces
        payload = """<admin_password>
                        TL0EfN33
                     </admin_password>"""
        expected = """<admin_password>***</admin_password>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'password' w/o spaces
        payload = """<password>TL0EfN33</password>"""
        expected = """<password>***</password>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'password' with spaces
        payload = """<password>
                        TL0EfN33
                     </password>"""
        expected = """<password>***</password>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'Password1' - case-insensitive + number
        payload = """<Password1>TL0EfN33</Password1>"""
        expected = """<Password1>***</Password1>"""
        self.assertEqual(expected, strutils.mask_password(payload))

    def test_xml_attribute(self):
        # Test 'adminPass' w/o spaces
        payload = """adminPass='TL0EfN33'"""
        expected = """adminPass='***'"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'adminPass' with spaces
        payload = """adminPass = 'TL0EfN33'"""
        expected = """adminPass = '***'"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'adminPass' with double quotes
        payload = """adminPass = "TL0EfN33\""""
        expected = """adminPass = "***\""""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_pass' w/o spaces
        payload = """admin_pass='TL0EfN33'"""
        expected = """admin_pass='***'"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_pass' with spaces
        payload = """admin_pass = 'TL0EfN33'"""
        expected = """admin_pass = '***'"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_pass' with double quotes
        payload = """admin_pass = "TL0EfN33\""""
        expected = """admin_pass = "***\""""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_password' w/o spaces
        payload = """admin_password='TL0EfN33'"""
        expected = """admin_password='***'"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_password' with spaces
        payload = """admin_password = 'TL0EfN33'"""
        expected = """admin_password = '***'"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'admin_password' with double quotes
        payload = """admin_password = "TL0EfN33\""""
        expected = """admin_password = "***\""""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'password' w/o spaces
        payload = """password='TL0EfN33'"""
        expected = """password='***'"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'password' with spaces
        payload = """password = 'TL0EfN33'"""
        expected = """password = '***'"""
        self.assertEqual(expected, strutils.mask_password(payload))
        # Test 'password' with double quotes
        payload = """password = "TL0EfN33\""""
        expected = """password = "***\""""
        self.assertEqual(expected, strutils.mask_password(payload))

    def test_json_message(self):
        payload = """body: {"changePassword": {"adminPass": "1234567"}}"""
        expected = """body: {"changePassword": {"adminPass": "***"}}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        payload = """body: {"rescue": {"admin_pass": "1234567"}}"""
        expected = """body: {"rescue": {"admin_pass": "***"}}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        payload = """body: {"rescue": {"admin_password": "1234567"}}"""
        expected = """body: {"rescue": {"admin_password": "***"}}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        payload = """body: {"rescue": {"password": "1234567"}}"""
        expected = """body: {"rescue": {"password": "***"}}"""
        self.assertEqual(expected, strutils.mask_password(payload))
        payload = """body: {"rescue": {"encryption_key_id": "1234567"}}"""
        expected = """body: {"rescue": {"encryption_key_id": "***"}}"""
        self.assertEqual(expected, strutils.mask_password(payload))

    def test_xml_message(self):
        payload = """<?xml version="1.0" encoding="UTF-8"?>
<rebuild
    xmlns="http://docs.openstack.org/compute/api/v1.1"
    name="foobar"
    imageRef="http://openstack.example.com/v1.1/32278/images/70a599e0-31e7"
    accessIPv4="1.2.3.4"
    accessIPv6="fe80::100"
    adminPass="seekr3t">
  <metadata>
    <meta key="My Server Name">Apache1</meta>
  </metadata>
</rebuild>"""
        expected = """<?xml version="1.0" encoding="UTF-8"?>
<rebuild
    xmlns="http://docs.openstack.org/compute/api/v1.1"
    name="foobar"
    imageRef="http://openstack.example.com/v1.1/32278/images/70a599e0-31e7"
    accessIPv4="1.2.3.4"
    accessIPv6="fe80::100"
    adminPass="***">
  <metadata>
    <meta key="My Server Name">Apache1</meta>
  </metadata>
</rebuild>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        payload = """<?xml version="1.0" encoding="UTF-8"?>
<rescue xmlns="http://docs.openstack.org/compute/api/v1.1"
    admin_pass="MySecretPass"/>"""
        expected = """<?xml version="1.0" encoding="UTF-8"?>
<rescue xmlns="http://docs.openstack.org/compute/api/v1.1"
    admin_pass="***"/>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        payload = """<?xml version="1.0" encoding="UTF-8"?>
<rescue xmlns="http://docs.openstack.org/compute/api/v1.1"
    admin_password="MySecretPass"/>"""
        expected = """<?xml version="1.0" encoding="UTF-8"?>
<rescue xmlns="http://docs.openstack.org/compute/api/v1.1"
    admin_password="***"/>"""
        self.assertEqual(expected, strutils.mask_password(payload))
        payload = """<?xml version="1.0" encoding="UTF-8"?>
<rescue xmlns="http://docs.openstack.org/compute/api/v1.1"
    password="MySecretPass"/>"""
        expected = """<?xml version="1.0" encoding="UTF-8"?>
<rescue xmlns="http://docs.openstack.org/compute/api/v1.1"
    password="***"/>"""
        self.assertEqual(expected, strutils.mask_password(payload))

    def test_mask_password(self):
        payload = "test = 'password'  :   'aaaaaa'"
        expected = "test = 'password'  :   '111'"
        self.assertEqual(expected,
                         strutils.mask_password(payload, secret='111'))

        payload = 'mysqld --password "aaaaaa"'
        expected = 'mysqld --password "****"'
        self.assertEqual(expected,
                         strutils.mask_password(payload, secret='****'))

        payload = 'mysqld --password aaaaaa'
        expected = 'mysqld --password ???'
        self.assertEqual(expected,
                         strutils.mask_password(payload, secret='???'))

        payload = 'mysqld --password = "aaaaaa"'
        expected = 'mysqld --password = "****"'
        self.assertEqual(expected,
                         strutils.mask_password(payload, secret='****'))

        payload = "mysqld --password = 'aaaaaa'"
        expected = "mysqld --password = '****'"
        self.assertEqual(expected,
                         strutils.mask_password(payload, secret='****'))

        payload = "mysqld --password = aaaaaa"
        expected = "mysqld --password = ****"
        self.assertEqual(expected,
                         strutils.mask_password(payload, secret='****'))

        payload = "test = password =   aaaaaa"
        expected = "test = password =   111"
        self.assertEqual(expected,
                         strutils.mask_password(payload, secret='111'))

        payload = "test = password=   aaaaaa"
        expected = "test = password=   111"
        self.assertEqual(expected,
                         strutils.mask_password(payload, secret='111'))

        payload = "test = password =aaaaaa"
        expected = "test = password =111"
        self.assertEqual(expected,
                         strutils.mask_password(payload, secret='111'))

        payload = "test = password=aaaaaa"
        expected = "test = password=111"
        self.assertEqual(expected,
                         strutils.mask_password(payload, secret='111'))

        payload = 'test = "original_password" : "aaaaaaaaa"'
        expected = 'test = "original_password" : "***"'
        self.assertEqual(expected, strutils.mask_password(payload))

        payload = 'test = "param1" : "value"'
        expected = 'test = "param1" : "value"'
        self.assertEqual(expected, strutils.mask_password(payload))

        payload = """{'adminPass':'TL0EfN33'}"""
        payload = six.text_type(payload)
        expected = """{'adminPass':'***'}"""
        self.assertEqual(expected, strutils.mask_password(payload))

        payload = """{'token':'mytoken'}"""
        payload = six.text_type(payload)
        expected = """{'token':'***'}"""
        self.assertEqual(expected, strutils.mask_password(payload))

        payload = ("test = 'node.session.auth.password','-v','TL0EfN33',"
                   "'nomask'")
        expected = ("test = 'node.session.auth.password','-v','***',"
                    "'nomask'")
        self.assertEqual(expected, strutils.mask_password(payload))

        payload = ("test = 'node.session.auth.password', '--password', "
                   "'TL0EfN33', 'nomask'")
        expected = ("test = 'node.session.auth.password', '--password', "
                    "'***', 'nomask'")
        self.assertEqual(expected, strutils.mask_password(payload))

        payload = ("test = 'node.session.auth.password', '--password', "
                   "'TL0EfN33'")
        expected = ("test = 'node.session.auth.password', '--password', "
                    "'***'")
        self.assertEqual(expected, strutils.mask_password(payload))

        payload = "test = node.session.auth.password -v TL0EfN33 nomask"
        expected = "test = node.session.auth.password -v *** nomask"
        self.assertEqual(expected, strutils.mask_password(payload))

        payload = ("test = node.session.auth.password --password TL0EfN33 "
                   "nomask")
        expected = ("test = node.session.auth.password --password *** "
                    "nomask")
        self.assertEqual(expected, strutils.mask_password(payload))

        payload = ("test = node.session.auth.password --password TL0EfN33")
        expected = ("test = node.session.auth.password --password ***")
        self.assertEqual(expected, strutils.mask_password(payload))

        payload = "test = cmd --password my\xe9\x80\x80pass"
        expected = ("test = cmd --password ***")
        self.assertEqual(expected, strutils.mask_password(payload))


class TestMapping(collections.Mapping):
    """Test class for non-dict mappings"""
    def __init__(self):
        super(TestMapping, self).__init__()
        self.data = {'password': 'shhh',
                     'foo': 'bar',
                     }

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return len(self.data)


class NestedMapping(TestMapping):
    """Test class that contains an instance of TestMapping"""
    def __init__(self):
        super(NestedMapping, self).__init__()
        self.data = {'nested': TestMapping()}


class MaskDictionaryPasswordTestCase(test_base.BaseTestCase):

    def test_dictionary(self):
        payload = {'password': 'TL0EfN33'}
        expected = {'password': '***'}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

        payload = {'user': 'admin', 'password': 'TL0EfN33'}
        expected = {'user': 'admin', 'password': '***'}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

        payload = {'strval': 'somestring',
                   'dictval': {'user': 'admin', 'password': 'TL0EfN33'}}
        expected = {'strval': 'somestring',
                    'dictval': {'user': 'admin', 'password': '***'}}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

        payload = {'strval': '--password abc',
                   'dont_change': 'this is fine',
                   'dictval': {'user': 'admin', 'password': b'TL0EfN33'}}
        expected = {'strval': '--password ***',
                    'dont_change': 'this is fine',
                    'dictval': {'user': 'admin', 'password': '***'}}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

        payload = {'ipmi_password': 'KeDrahishvowphyecMornEm0or('}
        expected = {'ipmi_password': '***'}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

        payload = {'passwords': {'KeystoneFernetKey1': 'c5FijjS'}}
        expected = {'passwords': {'KeystoneFernetKey1': '***'}}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

        payload = {'passwords': {'keystonecredential0': 'c5FijjS'}}
        expected = {'passwords': {'keystonecredential0': '***'}}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

    def test_do_no_harm(self):
        payload = {}
        expected = {}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

        payload = {'somekey': 'somevalue',
                   'anotherkey': 'anothervalue'}
        expected = {'somekey': 'somevalue',
                    'anotherkey': 'anothervalue'}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

    def test_do_an_int(self):
        payload = {}
        payload[1] = 2
        expected = payload.copy()
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

    def test_mask_values(self):
        payload = {'somekey': 'test = cmd --password my\xe9\x80\x80pass'}
        expected = {'somekey': 'test = cmd --password ***'}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

    def test_other_non_str_values(self):
        payload = {'password': 'DK0PK1AK3', 'bool': True,
                   'dict': {'cat': 'meow', 'password': "*aa38skdjf"},
                   'float': 0.1, 'int': 123, 'list': [1, 2], 'none': None,
                   'str': 'foo'}
        expected = {'password': '***', 'bool': True,
                    'dict': {'cat': 'meow', 'password': '***'},
                    'float': 0.1, 'int': 123, 'list': [1, 2], 'none': None,
                    'str': 'foo'}
        self.assertEqual(expected,
                         strutils.mask_dict_password(payload))

    def test_argument_untouched(self):
        """Make sure that the argument passed in is not modified"""
        payload = {'password': 'DK0PK1AK3', 'bool': True,
                   'dict': {'cat': 'meow', 'password': "*aa38skdjf"},
                   'float': 0.1, 'int': 123, 'list': [1, 2], 'none': None,
                   'str': 'foo'}
        pristine = copy.deepcopy(payload)
        # Send the payload into the function, to see if it gets modified
        strutils.mask_dict_password(payload)
        self.assertEqual(pristine, payload)

    def test_non_dict(self):
        expected = {'password': '***',
                    'foo': 'bar',
                    }
        payload = TestMapping()
        self.assertEqual(expected, strutils.mask_dict_password(payload))

    def test_nested_non_dict(self):
        expected = {'nested': {'password': '***',
                               'foo': 'bar',
                               }
                    }
        payload = NestedMapping()
        self.assertEqual(expected, strutils.mask_dict_password(payload))


class IsIntLikeTestCase(test_base.BaseTestCase):
    def test_is_int_like_true(self):
        self.assertTrue(strutils.is_int_like(1))
        self.assertTrue(strutils.is_int_like("1"))
        self.assertTrue(strutils.is_int_like("514"))
        self.assertTrue(strutils.is_int_like("0"))

    def test_is_int_like_false(self):
        self.assertFalse(strutils.is_int_like(1.1))
        self.assertFalse(strutils.is_int_like("1.1"))
        self.assertFalse(strutils.is_int_like("1.1.1"))
        self.assertFalse(strutils.is_int_like(None))
        self.assertFalse(strutils.is_int_like("0."))
        self.assertFalse(strutils.is_int_like("aaaaaa"))
        self.assertFalse(strutils.is_int_like("...."))
        self.assertFalse(strutils.is_int_like("1g"))
        self.assertFalse(
            strutils.is_int_like("0cc3346e-9fef-4445-abe6-5d2b2690ec64"))
        self.assertFalse(strutils.is_int_like("a1"))
        # NOTE(viktors): 12e3 - is a float number
        self.assertFalse(strutils.is_int_like("12e3"))
        # NOTE(viktors): Check integer numbers with base not 10
        self.assertFalse(strutils.is_int_like("0o51"))
        self.assertFalse(strutils.is_int_like("0xDEADBEEF"))


class StringLengthTestCase(test_base.BaseTestCase):
    def test_check_string_length(self):
        self.assertIsNone(strutils.check_string_length(
                          'test', 'name', max_length=255))
        self.assertRaises(ValueError,
                          strutils.check_string_length,
                          '', 'name', min_length=1)
        self.assertRaises(ValueError,
                          strutils.check_string_length,
                          'a' * 256, 'name', max_length=255)
        self.assertRaises(TypeError,
                          strutils.check_string_length,
                          11, 'name', max_length=255)
        self.assertRaises(TypeError,
                          strutils.check_string_length,
                          dict(), 'name', max_length=255)

    def test_check_string_length_noname(self):
        self.assertIsNone(strutils.check_string_length(
                          'test', max_length=255))
        self.assertRaises(ValueError,
                          strutils.check_string_length,
                          '', min_length=1)
        self.assertRaises(ValueError,
                          strutils.check_string_length,
                          'a' * 256, max_length=255)
        self.assertRaises(TypeError,
                          strutils.check_string_length,
                          11, max_length=255)
        self.assertRaises(TypeError,
                          strutils.check_string_length,
                          dict(), max_length=255)


class SplitPathTestCase(test_base.BaseTestCase):
    def test_split_path_failed(self):
        self.assertRaises(ValueError, strutils.split_path, '')
        self.assertRaises(ValueError, strutils.split_path, '/')
        self.assertRaises(ValueError, strutils.split_path, '//')
        self.assertRaises(ValueError, strutils.split_path, '//a')
        self.assertRaises(ValueError, strutils.split_path, '/a/c')
        self.assertRaises(ValueError, strutils.split_path, '//c')
        self.assertRaises(ValueError, strutils.split_path, '/a/c/')
        self.assertRaises(ValueError, strutils.split_path, '/a//')
        self.assertRaises(ValueError, strutils.split_path, '/a', 2)
        self.assertRaises(ValueError, strutils.split_path, '/a', 2, 3)
        self.assertRaises(ValueError, strutils.split_path, '/a', 2, 3, True)
        self.assertRaises(ValueError, strutils.split_path, '/a/c/o/r', 3, 3)
        self.assertRaises(ValueError, strutils.split_path, '/a', 5, 4)

    def test_split_path_success(self):
        self.assertEqual(strutils.split_path('/a'), ['a'])
        self.assertEqual(strutils.split_path('/a/'), ['a'])
        self.assertEqual(strutils.split_path('/a/c', 2), ['a', 'c'])
        self.assertEqual(strutils.split_path('/a/c/o', 3), ['a', 'c', 'o'])
        self.assertEqual(strutils.split_path('/a/c/o/r', 3, 3, True),
                         ['a', 'c', 'o/r'])
        self.assertEqual(strutils.split_path('/a/c', 2, 3, True),
                         ['a', 'c', None])
        self.assertEqual(strutils.split_path('/a/c/', 2), ['a', 'c'])
        self.assertEqual(strutils.split_path('/a/c/', 2, 3), ['a', 'c', ''])

    def test_split_path_invalid_path(self):
        try:
            strutils.split_path('o\nn e', 2)
        except ValueError as err:
            self.assertEqual(str(err), 'Invalid path: o%0An%20e')
        try:
            strutils.split_path('o\nn e', 2, 3, True)
        except ValueError as err:
            self.assertEqual(str(err), 'Invalid path: o%0An%20e')


class SplitByCommas(test_base.BaseTestCase):
    def test_not_closed_quotes(self):
        self.assertRaises(ValueError, strutils.split_by_commas, '"ab","b""')

    def test_no_comma_before_opening_quotes(self):
        self.assertRaises(ValueError, strutils.split_by_commas, '"ab""b"')

    def test_quote_inside_unquoted(self):
        self.assertRaises(ValueError, strutils.split_by_commas, 'a"b,cd')

    def check(self, expect, input):
        self.assertEqual(expect, strutils.split_by_commas(input))

    def test_plain(self):
        self.check(["a,b", "ac"], '"a,b",ac')

    def test_with_backslash_inside_quoted(self):
        self.check(['abc"', 'de', 'fg,h', 'klm\\', '"nop'],
                   r'"abc\"","de","fg,h","klm\\","\"nop"')

    def test_with_backslash_inside_unquoted(self):
        self.check([r'a\bc', 'de'], r'a\bc,de')

    def test_with_escaped_quotes_in_row_inside_quoted(self):
        self.check(['a"b""c', 'd'], r'"a\"b\"\"c",d')


@ddt.ddt
class ValidateIntegerTestCase(test_base.BaseTestCase):

    @ddt.unpack
    @ddt.data({"value": 42, "name": "answer", "output": 42},
              {"value": "42", "name": "answer", "output": 42},
              {"value": "7", "name": "lucky", "output": 7,
               "min_value": 7, "max_value": 8},
              {"value": 7, "name": "lucky", "output": 7,
               "min_value": 6, "max_value": 7},
              {"value": 300, "name": "Spartaaa!!!", "output": 300,
               "min_value": 300},
              {"value": "300", "name": "Spartaaa!!!", "output": 300,
               "max_value": 300})
    def test_valid_inputs(self, output, value, name, **kwargs):
        self.assertEqual(strutils.validate_integer(value, name,
                                                   **kwargs), output)

    @ddt.unpack
    @ddt.data({"value": "im-not-an-int", "name": ''},
              {"value": 3.14, "name": "Pie"},
              {"value": "299", "name": "Sparta no-show",
               "min_value": 300, "max_value": 300},
              {"value": 55, "name": "doing 55 in a 54",
               "max_value": 54},
              {"value": six.unichr(129), "name": "UnicodeError",
               "max_value": 1000})
    def test_invalid_inputs(self, value, name, **kwargs):
        self.assertRaises(ValueError, strutils.validate_integer,
                          value, name, **kwargs)
