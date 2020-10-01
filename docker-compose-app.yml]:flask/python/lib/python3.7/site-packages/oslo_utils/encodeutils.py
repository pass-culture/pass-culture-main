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

import sys

import six


# NOTE(blk-u): This provides a symbol that can be overridden just for this
# module during testing. sys.getfilesystemencoding() is called by coverage so
# mocking it globally caused the coverage job to fail.
_getfilesystemencoding = sys.getfilesystemencoding


def safe_decode(text, incoming=None, errors='strict'):
    """Decodes incoming text/bytes string using `incoming` if they're not
       already unicode.

    :param incoming: Text's current encoding
    :param errors: Errors handling policy. See here for valid
        values http://docs.python.org/2/library/codecs.html
    :returns: text or a unicode `incoming` encoded
                representation of it.
    :raises TypeError: If text is not an instance of str
    """
    if not isinstance(text, (six.string_types, six.binary_type)):
        raise TypeError("%s can't be decoded" % type(text))

    if isinstance(text, six.text_type):
        return text

    if not incoming:
        incoming = (getattr(sys.stdin, 'encoding', None) or
                    sys.getdefaultencoding())

    try:
        return text.decode(incoming, errors)
    except UnicodeDecodeError:
        # Note(flaper87) If we get here, it means that
        # sys.stdin.encoding / sys.getdefaultencoding
        # didn't return a suitable encoding to decode
        # text. This happens mostly when global LANG
        # var is not set correctly and there's no
        # default encoding. In this case, most likely
        # python will use ASCII or ANSI encoders as
        # default encodings but they won't be capable
        # of decoding non-ASCII characters.
        #
        # Also, UTF-8 is being used since it's an ASCII
        # extension.
        return text.decode('utf-8', errors)


def safe_encode(text, incoming=None,
                encoding='utf-8', errors='strict'):
    """Encodes incoming text/bytes string using `encoding`.

    If incoming is not specified, text is expected to be encoded with
    current python's default encoding. (`sys.getdefaultencoding`)

    :param incoming: Text's current encoding
    :param encoding: Expected encoding for text (Default UTF-8)
    :param errors: Errors handling policy. See here for valid
        values http://docs.python.org/2/library/codecs.html
    :returns: text or a bytestring `encoding` encoded
                representation of it.
    :raises TypeError: If text is not an instance of str

    See also to_utf8() function which is simpler and don't depend on
    the locale encoding.
    """
    if not isinstance(text, (six.string_types, six.binary_type)):
        raise TypeError("%s can't be encoded" % type(text))

    if not incoming:
        incoming = (getattr(sys.stdin, 'encoding', None) or
                    sys.getdefaultencoding())

    # Avoid case issues in comparisons
    if hasattr(incoming, 'lower'):
        incoming = incoming.lower()
    if hasattr(encoding, 'lower'):
        encoding = encoding.lower()

    if isinstance(text, six.text_type):
        return text.encode(encoding, errors)
    elif text and encoding != incoming:
        # Decode text before encoding it with `encoding`
        text = safe_decode(text, incoming, errors)
        return text.encode(encoding, errors)
    else:
        return text


def to_utf8(text):
    """Encode Unicode to UTF-8, return bytes unchanged.

    Raise TypeError if text is not a bytes string or a Unicode string.

    .. versionadded:: 3.5
    """
    if isinstance(text, six.binary_type):
        return text
    elif isinstance(text, six.text_type):
        return text.encode('utf-8')
    else:
        raise TypeError("bytes or Unicode expected, got %s"
                        % type(text).__name__)


def exception_to_unicode(exc):
    """Get the message of an exception as a Unicode string.

    On Python 3, the exception message is always a Unicode string. On
    Python 2, the exception message is a bytes string *most* of the time.

    If the exception message is a bytes strings, try to decode it from UTF-8
    (superset of ASCII), from the locale encoding, or fallback to decoding it
    from ISO-8859-1 (which never fails).

    .. versionadded:: 1.6
    """
    msg = None
    if six.PY2:
        # First try by calling the unicode type constructor. We should try
        # unicode() before exc.__unicode__() because subclasses of unicode can
        # be easily casted to unicode, whereas they have no __unicode__()
        # method.
        try:
            msg = unicode(exc)  # NOQA
        except UnicodeError:
            # unicode(exc) fail with UnicodeDecodeError on Python 2 if
            # exc.__unicode__() or exc.__str__() returns a bytes string not
            # decodable from the default encoding (ASCII)
            if hasattr(exc, '__unicode__'):
                # Call directly the __unicode__() method to avoid
                # the implicit decoding from the default encoding
                try:
                    msg = exc.__unicode__()
                except UnicodeError:  # nosec
                    pass

    if msg is None:
        # Don't call directly str(exc), because it fails with
        # UnicodeEncodeError on Python 2 if exc.__str__() returns a Unicode
        # string not encodable to the default encoding (ASCII)
        msg = exc.__str__()

    if isinstance(msg, six.text_type):
        # This should be the default path on Python 3 and an *optional* path
        # on Python 2 (if for some reason the exception message was already
        # in unicode instead of the more typical bytes string); so avoid
        # further converting to unicode in both of these cases.
        return msg

    try:
        # Try to decode from UTF-8 (superset of ASCII). The decoder fails
        # if the string is not a valid UTF-8 string: the UTF-8 codec includes
        # a validation algorithm to ensure the consistency of the codec.
        return msg.decode('utf-8')
    except UnicodeDecodeError:  # nosec
        pass

    # Try the locale encoding, most error messages are encoded to this encoding
    # (ex: os.strerror(errno))
    encoding = _getfilesystemencoding()
    try:
        return msg.decode(encoding)
    except UnicodeDecodeError:  # nosec
        pass

    # The encoding is not ASCII, not UTF-8, nor the locale encoding. Fallback
    # to the ISO-8859-1 encoding which never fails. It will produce mojibake
    # if the message is not encoded to ISO-8859-1, but we don't want a super
    # complex heuristic to get the encoding of an exception message.
    return msg.decode('latin1')
