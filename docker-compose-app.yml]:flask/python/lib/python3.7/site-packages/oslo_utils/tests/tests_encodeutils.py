# -*- coding: utf-8 -*-

# Copyright 2014 Red Hat, Inc.
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

from unittest import mock

from oslo_i18n import fixture as oslo_i18n_fixture
from oslotest import base as test_base
import six
import testtools

from oslo_utils import encodeutils


class EncodeUtilsTest(test_base.BaseTestCase):

    def test_safe_decode(self):
        safe_decode = encodeutils.safe_decode
        self.assertRaises(TypeError, safe_decode, True)
        self.assertEqual(six.u('ni\xf1o'), safe_decode(six.b("ni\xc3\xb1o"),
                         incoming="utf-8"))
        if six.PY2:
            # In Python 3, bytes.decode() doesn't support anymore
            # bytes => bytes encodings like base64
            self.assertEqual(six.u("test"), safe_decode("dGVzdA==",
                             incoming='base64'))

        self.assertEqual(six.u("strange"), safe_decode(six.b('\x80strange'),
                         errors='ignore'))

        self.assertEqual(six.u('\xc0'), safe_decode(six.b('\xc0'),
                         incoming='iso-8859-1'))

        # Forcing incoming to ascii so it falls back to utf-8
        self.assertEqual(six.u('ni\xf1o'), safe_decode(six.b('ni\xc3\xb1o'),
                         incoming='ascii'))

        self.assertEqual(six.u('foo'), safe_decode(b'foo'))

    def test_safe_encode_none_instead_of_text(self):
        self.assertRaises(TypeError, encodeutils.safe_encode, None)

    def test_safe_encode_bool_instead_of_text(self):
        self.assertRaises(TypeError, encodeutils.safe_encode, True)

    def test_safe_encode_int_instead_of_text(self):
        self.assertRaises(TypeError, encodeutils.safe_encode, 1)

    def test_safe_encode_list_instead_of_text(self):
        self.assertRaises(TypeError, encodeutils.safe_encode, [])

    def test_safe_encode_dict_instead_of_text(self):
        self.assertRaises(TypeError, encodeutils.safe_encode, {})

    def test_safe_encode_tuple_instead_of_text(self):
        self.assertRaises(TypeError, encodeutils.safe_encode, ('foo', 'bar', ))

    def test_safe_encode_py2(self):
        if six.PY2:
            # In Python 3, str.encode() doesn't support anymore
            # text => text encodings like base64
            self.assertEqual(
                six.b("dGVzdA==\n"),
                encodeutils.safe_encode("test", encoding='base64'),
            )
        else:
            self.skipTest("Requires py2.x")

    def test_safe_encode_force_incoming_utf8_to_ascii(self):
        # Forcing incoming to ascii so it falls back to utf-8
        self.assertEqual(
            six.b('ni\xc3\xb1o'),
            encodeutils.safe_encode(six.b('ni\xc3\xb1o'), incoming='ascii'),
        )

    def test_safe_encode_same_encoding_different_cases(self):
        with mock.patch.object(encodeutils, 'safe_decode', mock.Mock()):
            utf8 = encodeutils.safe_encode(
                six.u('foo\xf1bar'), encoding='utf-8')
            self.assertEqual(
                encodeutils.safe_encode(utf8, 'UTF-8', 'utf-8'),
                encodeutils.safe_encode(utf8, 'utf-8', 'UTF-8'),
            )
            self.assertEqual(
                encodeutils.safe_encode(utf8, 'UTF-8', 'utf-8'),
                encodeutils.safe_encode(utf8, 'utf-8', 'utf-8'),
            )
            encodeutils.safe_decode.assert_has_calls([])

    def test_safe_encode_different_encodings(self):
        text = six.u('foo\xc3\xb1bar')
        result = encodeutils.safe_encode(
            text=text, incoming='utf-8', encoding='iso-8859-1')
        self.assertNotEqual(text, result)
        self.assertNotEqual(six.b("foo\xf1bar"), result)

    def test_to_utf8(self):
        self.assertEqual(encodeutils.to_utf8(b'a\xe9\xff'),        # bytes
                         b'a\xe9\xff')
        self.assertEqual(encodeutils.to_utf8(u'a\xe9\xff\u20ac'),  # Unicode
                         b'a\xc3\xa9\xc3\xbf\xe2\x82\xac')
        self.assertRaises(TypeError, encodeutils.to_utf8, 123)     # invalid

        # oslo.i18n Message objects should also be accepted for convenience.
        # It works because Message is a subclass of six.text_type. Use the
        # lazy translation to get a Message instance of oslo_i18n.
        msg = oslo_i18n_fixture.Translation().lazy("test")
        self.assertEqual(encodeutils.to_utf8(msg),
                         b'test')


class ExceptionToUnicodeTest(test_base.BaseTestCase):

    def test_str_exception(self):
        # The regular Exception class cannot be used directly:
        # Exception(u'\xe9').__str__() raises an UnicodeEncodeError
        # on Python 2
        class StrException(Exception):
            def __init__(self, value):
                Exception.__init__(self)
                self.value = value

            def __str__(self):
                return self.value

        # On Python 3, an exception which returns bytes with is __str__()
        # method (like StrException(bytes)) is probably a bug, but it was not
        # harder to support this silly case in exception_to_unicode().

        # Decode from ASCII
        exc = StrException(b'bytes ascii')
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u'bytes ascii')

        # Decode from UTF-8
        exc = StrException(b'utf-8 \xc3\xa9\xe2\x82\xac')
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u'utf-8 \xe9\u20ac')

        # Force the locale encoding to ASCII to test the fallback
        with mock.patch.object(encodeutils, '_getfilesystemencoding',
                               return_value='ascii'):
            # Fallback: decode from ISO-8859-1
            exc = StrException(b'rawbytes \x80\xff')
            self.assertEqual(encodeutils.exception_to_unicode(exc),
                             u'rawbytes \x80\xff')

        # No conversion needed
        exc = StrException(u'unicode ascii')
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u'unicode ascii')

        # No conversion needed
        exc = StrException(u'unicode \xe9\u20ac')
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u'unicode \xe9\u20ac')

        # Test the locale encoding
        with mock.patch.object(encodeutils, '_getfilesystemencoding',
                               return_value='koi8_r'):
            exc = StrException(b'\xf2\xd5\xd3\xd3\xcb\xc9\xca')
            # Decode from the locale encoding
            # (the message cannot be decoded from ASCII nor UTF-8)
            self.assertEqual(encodeutils.exception_to_unicode(exc),
                             u'\u0420\u0443\u0441\u0441\u043a\u0438\u0439')

    @testtools.skipIf(six.PY3, 'test specific to Python 2')
    def test_unicode_exception(self):
        # Exception with a __unicode__() method, but no __str__()
        class UnicodeException(Exception):
            def __init__(self, value):
                Exception.__init__(self)
                self.value = value

            def __unicode__(self):
                return self.value

        # __unicode__() returns unicode
        exc = UnicodeException(u'unicode \xe9\u20ac')
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u'unicode \xe9\u20ac')

        # __unicode__() returns bytes (does this case really happen in the
        # wild?)
        exc = UnicodeException(b'utf-8 \xc3\xa9\xe2\x82\xac')
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u'utf-8 \xe9\u20ac')

    @testtools.skipIf(six.PY3, 'test specific to Python 2')
    def test_unicode_or_str_exception(self):
        # Exception with __str__() and __unicode__() methods
        class UnicodeOrStrException(Exception):
            def __init__(self, unicode_value, str_value):
                Exception.__init__(self)
                self.unicode_value = unicode_value
                self.str_value = str_value

            def __unicode__(self):
                return self.unicode_value

            def __str__(self):
                return self.str_value

        # __unicode__() returns unicode
        exc = UnicodeOrStrException(u'unicode \xe9\u20ac', b'str')
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u'unicode \xe9\u20ac')

        # __unicode__() returns bytes (does this case really happen in the
        # wild?)
        exc = UnicodeOrStrException(b'utf-8 \xc3\xa9\xe2\x82\xac', b'str')
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u'utf-8 \xe9\u20ac')

    @testtools.skipIf(six.PY3, 'test specific to Python 2')
    def test_unicode_only_exception(self):
        # Exception with a __unicode__() method and a __str__() which
        # raises an exception (similar to the Message class of oslo_i18n)
        class UnicodeOnlyException(Exception):
            def __init__(self, value):
                Exception.__init__(self)
                self.value = value

            def __unicode__(self):
                return self.value

            def __str__(self):
                raise UnicodeError("use unicode()")

        # __unicode__() returns unicode
        exc = UnicodeOnlyException(u'unicode \xe9\u20ac')
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u'unicode \xe9\u20ac')

        # __unicode__() returns bytes
        exc = UnicodeOnlyException(b'utf-8 \xc3\xa9\xe2\x82\xac')
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u'utf-8 \xe9\u20ac')

    def test_oslo_i18n_message(self):
        # use the lazy translation to get a Message instance of oslo_i18n
        exc = oslo_i18n_fixture.Translation().lazy("test")
        self.assertEqual(encodeutils.exception_to_unicode(exc),
                         u"test")
