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

"""
System-level utilities and helper functions.
"""

import collections
import math
import re
import unicodedata

import pyparsing as pp
import six
from six.moves import urllib

from oslo_utils._i18n import _
from oslo_utils import encodeutils


UNIT_PREFIX_EXPONENT = {
    'k': 1,
    'K': 1,
    'Ki': 1,
    'M': 2,
    'Mi': 2,
    'G': 3,
    'Gi': 3,
    'T': 4,
    'Ti': 4,
}
UNIT_SYSTEM_INFO = {
    'IEC': (1024, re.compile(r'(^[-+]?\d*\.?\d+)([KMGT]i?)?(b|bit|B)$')),
    'SI': (1000, re.compile(r'(^[-+]?\d*\.?\d+)([kMGT])?(b|bit|B)$')),
    'mixed': (None, re.compile(r'(^[-+]?\d*\.?\d+)([kKMGT]i?)?(b|bit|B)$')),
}

TRUE_STRINGS = ('1', 't', 'true', 'on', 'y', 'yes')
FALSE_STRINGS = ('0', 'f', 'false', 'off', 'n', 'no')

SLUGIFY_STRIP_RE = re.compile(r"[^\w\s-]")
SLUGIFY_HYPHENATE_RE = re.compile(r"[-\s]+")


# NOTE(flaper87): The following globals are used by `mask_password` and
#                 `mask_dict_password`. They must all be lowercase.
_SANITIZE_KEYS = ['adminpass', 'admin_pass', 'password', 'admin_password',
                  'auth_token', 'new_pass', 'auth_password', 'secret_uuid',
                  'secret', 'sys_pswd', 'token', 'configdrive',
                  'chappassword', 'encrypted_key', 'private_key',
                  'encryption_key_id', 'fernetkey', 'sslkey', 'passphrase',
                  'cephclusterfsid', 'octaviaheartbeatkey', 'rabbitcookie',
                  'cephmanilaclientkey', 'pacemakerremoteauthkey',
                  'designaterndckey', 'cephadminkey', 'heatauthencryptionkey',
                  'cephclientkey', 'keystonecredential',
                  'barbicansimplecryptokek', 'cephrgwkey', 'swifthashsuffix',
                  'migrationsshkey', 'cephmdskey', 'cephmonkey']

# NOTE(ldbragst): Let's build a list of regex objects using the list of
# _SANITIZE_KEYS we already have. This way, we only have to add the new key
# to the list of _SANITIZE_KEYS and we can generate regular expressions
# for XML and JSON automatically.
_SANITIZE_PATTERNS_2 = {}
_SANITIZE_PATTERNS_1 = {}

# NOTE(amrith): Some regular expressions have only one parameter, some
# have two parameters. Use different lists of patterns here.
_FORMAT_PATTERNS_1 = [r'(%(key)s[0-9]*\s*[=]\s*)[^\s^\'^\"]+']
_FORMAT_PATTERNS_2 = [r'(%(key)s[0-9]*\s*[=]\s*[\"\'])[^\"\']*([\"\'])',
                      r'(%(key)s[0-9]*\s+[\"\'])[^\"\']*([\"\'])',
                      r'([-]{2}%(key)s[0-9]*\s+)[^\'^\"^=^\s]+([\s]*)',
                      r'(<%(key)s[0-9]*>)[^<]*(</%(key)s[0-9]*>)',
                      r'([\"\']%(key)s[0-9]*[\"\']\s*:\s*[\"\'])[^\"\']*'
                      r'([\"\'])',
                      r'([\'"][^"\']*%(key)s[0-9]*[\'"]\s*:\s*u?[\'"])[^\"\']*'
                      r'([\'"])',
                      r'([\'"][^\'"]*%(key)s[0-9]*[\'"]\s*,\s*\'--?[A-z]+'
                      r'\'\s*,\s*u?[\'"])[^\"\']*([\'"])',
                      r'(%(key)s[0-9]*\s*--?[A-z]+\s*)\S+(\s*)']

# NOTE(dhellmann): Keep a separate list of patterns by key so we only
# need to apply the substitutions for keys we find using a quick "in"
# test.
for key in _SANITIZE_KEYS:
    _SANITIZE_PATTERNS_1[key] = []
    _SANITIZE_PATTERNS_2[key] = []

    for pattern in _FORMAT_PATTERNS_2:
        reg_ex = re.compile(pattern % {'key': key}, re.DOTALL | re.IGNORECASE)
        _SANITIZE_PATTERNS_2[key].append(reg_ex)

    for pattern in _FORMAT_PATTERNS_1:
        reg_ex = re.compile(pattern % {'key': key}, re.DOTALL | re.IGNORECASE)
        _SANITIZE_PATTERNS_1[key].append(reg_ex)


def int_from_bool_as_string(subject):
    """Interpret a string as a boolean and return either 1 or 0.

    Any string value in:

        ('True', 'true', 'On', 'on', '1')

    is interpreted as a boolean True.

    Useful for JSON-decoded stuff and config file parsing
    """
    return int(bool_from_string(subject))


def bool_from_string(subject, strict=False, default=False):
    """Interpret a subject as a boolean.

    A subject can be a boolean, a string or an integer. Boolean type value
    will be returned directly, otherwise the subject will be converted to
    a string. A case-insensitive match is performed such that strings
    matching 't','true', 'on', 'y', 'yes', or '1' are considered True and,
    when `strict=False`, anything else returns the value specified by
    'default'.

    Useful for JSON-decoded stuff and config file parsing.

    If `strict=True`, unrecognized values, including None, will raise a
    ValueError which is useful when parsing values passed in from an API call.
    Strings yielding False are 'f', 'false', 'off', 'n', 'no', or '0'.
    """
    if isinstance(subject, bool):
        return subject
    if not isinstance(subject, six.string_types):
        subject = six.text_type(subject)

    lowered = subject.strip().lower()

    if lowered in TRUE_STRINGS:
        return True
    elif lowered in FALSE_STRINGS:
        return False
    elif strict:
        acceptable = ', '.join(
            "'%s'" % s for s in sorted(TRUE_STRINGS + FALSE_STRINGS))
        msg = _("Unrecognized value '%(val)s', acceptable values are:"
                " %(acceptable)s") % {'val': subject,
                                      'acceptable': acceptable}
        raise ValueError(msg)
    else:
        return default


def is_valid_boolstr(value):
    """Check if the provided string is a valid bool string or not.

    :param value: value to verify
    :type value: string
    :returns: true if value is boolean string, false otherwise

    .. versionadded:: 3.17
    """
    boolstrs = TRUE_STRINGS + FALSE_STRINGS
    return str(value).lower() in boolstrs


def string_to_bytes(text, unit_system='IEC', return_int=False):
    """Converts a string into an float representation of bytes.

    The units supported for IEC / mixed::

        Kb(it), Kib(it), Mb(it), Mib(it), Gb(it), Gib(it), Tb(it), Tib(it)
        KB, KiB, MB, MiB, GB, GiB, TB, TiB

    The units supported for SI ::

        kb(it), Mb(it), Gb(it), Tb(it)
        kB, MB, GB, TB

    SI units are interpreted as power-of-ten (e.g. 1kb = 1000b).  Note
    that the SI unit system does not support capital letter 'K'

    IEC units are interpreted as power-of-two (e.g. 1MiB = 1MB =
    1024b)

    Mixed units interpret the "i" to mean IEC, and no "i" to mean SI
    (e.g. 1kb = 1000b, 1kib == 1024b).  Additionaly, mixed units
    interpret 'K' as power-of-ten.  This mode is not particuarly
    useful for new code, but can help with compatability for parsers
    such as GNU parted.

    :param text: String input for bytes size conversion.
    :param unit_system: Unit system for byte size conversion.
    :param return_int: If True, returns integer representation of text
                       in bytes. (default: decimal)
    :returns: Numerical representation of text in bytes.
    :raises ValueError: If text has an invalid value.

    """
    try:
        base, reg_ex = UNIT_SYSTEM_INFO[unit_system]
    except KeyError:
        msg = _('Invalid unit system: "%s"') % unit_system
        raise ValueError(msg)
    match = reg_ex.match(text)
    if match:
        magnitude = float(match.group(1))
        unit_prefix = match.group(2)
        if match.group(3) in ['b', 'bit']:
            magnitude /= 8

        # In the mixed matcher, IEC units (with a trailing 'i') are
        # interpreted as power-of-two, others as power-of-ten
        if unit_system == 'mixed':
            if unit_prefix and not unit_prefix.endswith('i'):
                # For maximum compatability in mixed mode, we understand
                # "K" (which is not strict SI) as "k"
                if unit_prefix.startswith == 'K':
                    unit_prefix = 'k'
                base = 1000
            else:
                base = 1024
    else:
        msg = _('Invalid string format: %s') % text
        raise ValueError(msg)

    if not unit_prefix:
        res = magnitude
    else:
        res = magnitude * pow(base, UNIT_PREFIX_EXPONENT[unit_prefix])
    if return_int:
        return int(math.ceil(res))
    return res


def to_slug(value, incoming=None, errors="strict"):
    """Normalize string.

    Convert to lowercase, remove non-word characters, and convert spaces
    to hyphens.

    Inspired by Django's `slugify` filter.

    :param value: Text to slugify
    :param incoming: Text's current encoding
    :param errors: Errors handling policy. See here for valid
        values http://docs.python.org/2/library/codecs.html
    :returns: slugified unicode representation of `value`
    :raises TypeError: If text is not an instance of str
    """
    value = encodeutils.safe_decode(value, incoming, errors)
    # NOTE(aababilov): no need to use safe_(encode|decode) here:
    # encodings are always "ascii", error handling is always "ignore"
    # and types are always known (first: unicode; second: str)
    value = unicodedata.normalize("NFKD", value).encode(
        "ascii", "ignore").decode("ascii")
    value = SLUGIFY_STRIP_RE.sub("", value).strip().lower()
    return SLUGIFY_HYPHENATE_RE.sub("-", value)


# NOTE(dhellmann): Before submitting a patch to add a new argument to
# this function to allow the caller to pass in "extra" or "additional"
# or "replacement" patterns to be masked out, please note that we have
# discussed that feature many times and always rejected it based on
# the desire to have Oslo functions behave consistently across all
# projects and *especially* to have security features work the same
# way no matter where they are used. If every project adopted its own
# set patterns for secret values, it would be very difficult to audit
# the logging to ensure that everything is properly masked. So, please
# either add your pattern to the module-level variables at the top of
# this file or, even better, pick an existing pattern or key to use in
# your application to ensure that the value is masked by this
# function.
def mask_password(message, secret="***"):  # nosec
    """Replace password with *secret* in message.

    :param message: The string which includes security information.
    :param secret: value with which to replace passwords.
    :returns: The unicode value of message with the password fields masked.

    For example:

    >>> mask_password("'adminPass' : 'aaaaa'")
    "'adminPass' : '***'"
    >>> mask_password("'admin_pass' : 'aaaaa'")
    "'admin_pass' : '***'"
    >>> mask_password('"password" : "aaaaa"')
    '"password" : "***"'
    >>> mask_password("'original_password' : 'aaaaa'")
    "'original_password' : '***'"
    >>> mask_password("u'original_password' :   u'aaaaa'")
    "u'original_password' :   u'***'"

    .. versionadded:: 0.2

    .. versionchanged:: 1.1
       Replace also ``'auth_token'``, ``'new_pass'`` and ``'auth_password'``
       keys.

    .. versionchanged:: 1.1.1
       Replace also ``'secret_uuid'`` key.

    .. versionchanged:: 1.5
       Replace also ``'sys_pswd'`` key.

    .. versionchanged:: 2.6
       Replace also ``'token'`` key.

    .. versionchanged:: 2.7
       Replace also ``'secret'`` key.

    .. versionchanged:: 3.4
       Replace also ``'configdrive'`` key.

    .. versionchanged:: 3.8
       Replace also ``'CHAPPASSWORD'`` key.
    """

    try:
        message = six.text_type(message)
    except UnicodeDecodeError:  # nosec
        # NOTE(jecarey): Temporary fix to handle cases where message is a
        # byte string. A better solution will be provided in Kilo.
        pass

    substitute1 = r'\g<1>' + secret
    substitute2 = r'\g<1>' + secret + r'\g<2>'

    # NOTE(ldbragst): Check to see if anything in message contains any key
    # specified in _SANITIZE_KEYS, if not then just return the message since
    # we don't have to mask any passwords.
    for key in _SANITIZE_KEYS:
        if key in message.lower():
            for pattern in _SANITIZE_PATTERNS_2[key]:
                message = re.sub(pattern, substitute2, message)
            for pattern in _SANITIZE_PATTERNS_1[key]:
                message = re.sub(pattern, substitute1, message)

    return message


def mask_dict_password(dictionary, secret="***"):  # nosec
    """Replace password with *secret* in a dictionary recursively.

    :param dictionary: The dictionary which includes secret information.
    :param secret: value with which to replace secret information.
    :returns: The dictionary with string substitutions.

    A dictionary (which may contain nested dictionaries) contains
    information (such as passwords) which should not be revealed, and
    this function helps detect and replace those with the 'secret'
    provided (or `***` if none is provided).

    Substitution is performed in one of three situations:

    If the key is something that is considered to be indicative of a
    secret, then the corresponding value is replaced with the secret
    provided (or `***` if none is provided).

    If a value in the dictionary is a string, then it is masked
    using the ``mask_password()`` function.

    Finally, if a value is a dictionary, this function will
    recursively mask that dictionary as well.

    For example:

    >>> mask_dict_password({'password': 'd81juxmEW_',
    >>>                     'user': 'admin',
    >>>                     'home-dir': '/home/admin'},
    >>>                     '???')
    {'password': '???', 'user': 'admin', 'home-dir': '/home/admin'}

    For example (the value is masked using mask_password())

    >>> mask_dict_password({'password': '--password d81juxmEW_',
    >>>                     'user': 'admin',
    >>>                     'home-dir': '/home/admin'},
    >>>                     '???')
    {'password': '--password ???', 'user': 'admin',
     'home-dir': '/home/admin'}


    For example (a nested dictionary is masked):

    >>> mask_dict_password({"nested": {'password': 'd81juxmEW_',
    >>>                     'user': 'admin',
    >>>                     'home': '/home/admin'}},
    >>>                     '???')
    {"nested": {'password': '???', 'user': 'admin', 'home': '/home/admin'}}

    .. versionadded:: 3.4

    """

    if not isinstance(dictionary, collections.Mapping):
        raise TypeError("Expected a Mapping, got %s instead."
                        % type(dictionary))
    out = {}
    for k, v in dictionary.items():
        if isinstance(v, collections.Mapping):
            out[k] = mask_dict_password(v, secret=secret)
            continue
        # NOTE(jlvillal): Check to see if anything in the dictionary 'key'
        # contains any key specified in _SANITIZE_KEYS.
        k_matched = False
        if isinstance(k, six.string_types):
            for sani_key in _SANITIZE_KEYS:
                if sani_key in k.lower():
                    out[k] = secret
                    k_matched = True
                    break
        if not k_matched:
            # We did not find a match for the key name in the
            # _SANITIZE_KEYS, so we fall through to here
            if isinstance(v, six.string_types):
                out[k] = mask_password(v, secret=secret)
            else:
                # Just leave it alone.
                out[k] = v
    return out


def is_int_like(val):
    """Check if a value looks like an integer with base 10.

    :param val: Value to verify
    :type val: string
    :returns: bool

    .. versionadded:: 1.1
    """
    try:
        return six.text_type(int(val)) == six.text_type(val)
    except (TypeError, ValueError):
        return False


def check_string_length(value, name=None, min_length=0, max_length=None):
    """Check the length of specified string.

    :param value: the value of the string
    :param name: the name of the string
    :param min_length: the min_length of the string
    :param max_length: the max_length of the string
    :raises TypeError, ValueError: For any invalid input.

    .. versionadded:: 3.7
    """
    if name is None:
        name = value

    if not isinstance(value, six.string_types):
        msg = _("%s is not a string or unicode") % name
        raise TypeError(msg)

    length = len(value)
    if length < min_length:
        msg = _("%(name)s has %(length)s characters, less than "
                "%(min_length)s.") % {'name': name, 'length': length,
                                      'min_length': min_length}
        raise ValueError(msg)

    if max_length and length > max_length:
        msg = _("%(name)s has %(length)s characters, more than "
                "%(max_length)s.") % {'name': name, 'length': length,
                                      'max_length': max_length}
        raise ValueError(msg)


def validate_integer(value, name, min_value=None, max_value=None):
    """Make sure that value is a valid integer, potentially within range.

    :param value: value of the integer
    :param name: name of the integer
    :param min_value: min_value of the integer
    :param max_value: max_value of the integer
    :returns: integer
    :raises: ValueError if value is an invalid integer

    .. versionadded:: 3.33
    """
    try:
        value = int(str(value))
    except (ValueError, UnicodeEncodeError):
        msg = _('%(value_name)s must be an integer'
                ) % {'value_name': name}
        raise ValueError(msg)

    if min_value is not None and value < min_value:
        msg = _('%(value_name)s must be >= %(min_value)d'
                ) % {'value_name': name, 'min_value': min_value}
        raise ValueError(msg)

    if max_value is not None and value > max_value:
        msg = _('%(value_name)s must be <= %(max_value)d'
                ) % {'value_name': name, 'max_value': max_value}
        raise ValueError(msg)

    return value


def split_path(path, minsegs=1, maxsegs=None, rest_with_last=False):
    """Validate and split the given HTTP request path.

    **Examples**::

        ['a'] = _split_path('/a')
        ['a', None] = _split_path('/a', 1, 2)
        ['a', 'c'] = _split_path('/a/c', 1, 2)
        ['a', 'c', 'o/r'] = _split_path('/a/c/o/r', 1, 3, True)

    :param path: HTTP Request path to be split
    :param minsegs: Minimum number of segments to be extracted
    :param maxsegs: Maximum number of segments to be extracted
    :param rest_with_last: If True, trailing data will be returned as part
                           of last segment.  If False, and there is
                           trailing data, raises ValueError.
    :returns: list of segments with a length of maxsegs (non-existent
              segments will return as None)
    :raises: ValueError if given an invalid path

    .. versionadded:: 3.11
    """
    if not maxsegs:
        maxsegs = minsegs
    if minsegs > maxsegs:
        raise ValueError(_('minsegs > maxsegs: %(min)d > %(max)d)') %
                         {'min': minsegs, 'max': maxsegs})
    if rest_with_last:
        segs = path.split('/', maxsegs)
        minsegs += 1
        maxsegs += 1
        count = len(segs)
        if (segs[0] or count < minsegs or count > maxsegs or
                '' in segs[1:minsegs]):
            raise ValueError(_('Invalid path: %s') % urllib.parse.quote(path))
    else:
        minsegs += 1
        maxsegs += 1
        segs = path.split('/', maxsegs)
        count = len(segs)
        if (segs[0] or count < minsegs or count > maxsegs + 1 or
                '' in segs[1:minsegs] or
                (count == maxsegs + 1 and segs[maxsegs])):
            raise ValueError(_('Invalid path: %s') % urllib.parse.quote(path))
    segs = segs[1:maxsegs]
    segs.extend([None] * (maxsegs - 1 - len(segs)))
    return segs


def split_by_commas(value):
    """Split values by commas and quotes according to api-wg

    :param value: value to be split

    .. versionadded:: 3.17
    """
    word = (pp.QuotedString(quoteChar='"', escChar='\\') |
            pp.Word(pp.printables, excludeChars='",'))
    grammar = pp.stringStart + pp.delimitedList(word) + pp.stringEnd

    try:
        return list(grammar.parseString(value))
    except pp.ParseException:
        raise ValueError("Invalid value: %s" % value)
