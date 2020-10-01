# Copyright 2013 Mirantis, Inc.
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

"""Type conversion and validation classes for configuration options.

Use these classes as values for the `type` argument to
:class:`oslo_config.cfg.Opt` and its subclasses.

.. versionadded:: 1.3
"""
import collections
import operator
import re
import warnings

import abc
from debtcollector import removals
import netaddr
import rfc3986


class ConfigType(object, metaclass=abc.ABCMeta):

    def __init__(self, type_name='unknown type'):
        self.type_name = type_name

    NONE_DEFAULT = '<None>'

    def format_defaults(self, default, sample_default=None):
        """Return a list of formatted default values.

        """
        if sample_default is not None:
            if isinstance(sample_default, str):
                default_str = sample_default
            else:
                default_str = self._formatter(sample_default)
        elif default is None:
            default_str = self.NONE_DEFAULT
        else:
            default_str = self._formatter(default)
        return [default_str]

    def quote_trailing_and_leading_space(self, str_val):
        if not isinstance(str_val, str):
            warnings.warn('converting \'%s\' to a string' % str_val)
            str_val = str(str_val)
        if str_val.strip() != str_val:
            return '"%s"' % str_val
        return str_val

    @abc.abstractmethod
    def _formatter(self, value):
        pass


class String(ConfigType):

    """String type.

    String values do not get transformed and are returned as str objects.

    :param choices: Optional sequence of either valid values or tuples of valid
        values with descriptions. Mutually exclusive with 'regex'.
    :param quotes: If True and string is enclosed with single or double
                   quotes, will strip those quotes. Will signal error if
                   string have quote at the beginning and no quote at
                   the end. Turned off by default. Useful if used with
                   container types like List.
    :param regex: Optional regular expression (string or compiled
                  regex) that the value must match on an unanchored
                  search. Mutually exclusive with 'choices'.
    :param ignore_case:  If True case differences (uppercase vs. lowercase)
                         between 'choices' or 'regex' will be ignored;
                         defaults to False.
    :param max_length:  Optional integer. If a positive value is specified,
                        a maximum length of an option value must be less than
                        or equal to this parameter. Otherwise no length check
                        will be done.
    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.1
       Added *regex* parameter.

    .. versionchanged:: 2.5
       Added *ignore_case* parameter.

    .. versionchanged:: 2.7
       Added *max_length* parameter.
       Added *type_name* parameter.

    .. versionchanged:: 5.2
       The *choices* parameter will now accept a sequence of tuples, where each
       tuple is of form (*choice*, *description*)
    """

    def __init__(self, choices=None, quotes=False, regex=None,
                 ignore_case=False, max_length=None,
                 type_name='string value'):
        super(String, self).__init__(type_name=type_name)
        if choices and regex:
            raise ValueError("'choices' and 'regex' cannot both be specified")

        self.ignore_case = ignore_case
        self.quotes = quotes
        self.max_length = max_length or 0

        if choices is not None:
            if not all(isinstance(choice, tuple) for choice in choices):
                choices = [(choice, None) for choice in choices]

            self.choices = collections.OrderedDict(choices)
        else:
            self.choices = None

        self.lower_case_choices = None
        if self.choices is not None and self.ignore_case:
            self.lower_case_choices = [c.lower() for c in self.choices]

        self.regex = regex
        if self.regex is not None:
            re_flags = re.IGNORECASE if self.ignore_case else 0

            # Check if regex is a string or an already compiled regex
            if isinstance(regex, str):
                self.regex = re.compile(regex, re_flags)
            else:
                self.regex = re.compile(regex.pattern, re_flags | regex.flags)

    def __call__(self, value):
        value = str(value)
        if self.quotes and value:
            if value[0] in "\"'":
                if len(value) == 1 or value[-1] != value[0]:
                    raise ValueError('Non-closed quote: %s' % value)
                value = value[1:-1]

        if self.max_length > 0 and len(value) > self.max_length:
            raise ValueError("Value '%s' exceeds maximum length %d" %
                             (value, self.max_length))

        if self.regex and not self.regex.search(value):
            raise ValueError("Value %r doesn't match regex %r" %
                             (value, self.regex.pattern))

        if self.choices is None:
            return value

        # Check for case insensitive
        processed_value, choices = ((value.lower(), self.lower_case_choices)
                                    if self.ignore_case else
                                    (value, self.choices.keys()))
        if processed_value in choices:
            return value

        raise ValueError(
            'Valid values are [%s], but found %s' % (
                ', '.join([str(v) for v in self.choices]),
                repr(value)))

    def __repr__(self):
        details = []
        if self.choices is not None:
            details.append("choices={!r}".format(list(self.choices.keys())))
        if self.regex:
            details.append("regex=%r" % self.regex.pattern)
        if details:
            return "String(%s)" % ",".join(details)
        return 'String'

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (self.quotes == other.quotes) and
            (self.regex == other.regex) and
            (set([x for x in self.choices or []]) ==
                set([x for x in other.choices or []]) if
             self.choices and other.choices else
             self.choices == other.choices)
        )

    def _formatter(self, value):
        return self.quote_trailing_and_leading_space(value)


class MultiString(String):
    """Multi-valued string."""

    def __init__(self, type_name='multi valued'):
        super(MultiString, self).__init__(type_name=type_name)

    NONE_DEFAULT = ['']

    def format_defaults(self, default, sample_default=None):
        """Return a list of formatted default values.

        """
        if sample_default is not None:
            default_list = self._formatter(sample_default)
        elif not default:
            default_list = self.NONE_DEFAULT
        else:
            default_list = self._formatter(default)
        return default_list

    def _formatter(self, value):
        return [self.quote_trailing_and_leading_space(v) for v in value]


class Boolean(ConfigType):

    """Boolean type.

    Values are case insensitive and can be set using
    1/0, yes/no, true/false or on/off.

    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.7

       Added *type_name* parameter.
    """
    TRUE_VALUES = ['true', '1', 'on', 'yes']
    FALSE_VALUES = ['false', '0', 'off', 'no']

    def __init__(self, type_name='boolean value'):
        super(Boolean, self).__init__(type_name=type_name)

    def __call__(self, value):
        if isinstance(value, bool):
            return value

        s = value.lower()
        if s in self.TRUE_VALUES:
            return True
        elif s in self.FALSE_VALUES:
            return False
        else:
            raise ValueError('Unexpected boolean value %r' % value)

    def __repr__(self):
        return 'Boolean'

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def _formatter(self, value):
        return str(value).lower()


class Number(ConfigType):

    """Number class, base for Integer and Float.

    :param num_type: the type of number used for casting (i.e int, float)
    :param type_name: Type name to be used in the sample config file.
    :param min: Optional check that value is greater than or equal to min.
    :param max: Optional check that value is less than or equal to max.
    :param choices: Optional sequence of either valid values or tuples of valid
        values with descriptions.

    .. versionadded:: 3.14

    .. versionchanged:: 5.2
       The *choices* parameter will now accept a sequence of tuples, where each
       tuple is of form (*choice*, *description*)
    """

    def __init__(self, num_type, type_name,
                 min=None, max=None, choices=None):
        super(Number, self).__init__(type_name=type_name)

        if min is not None and max is not None and max < min:
            raise ValueError('Max value is less than min value')

        if choices is not None:
            if not all(isinstance(choice, tuple) for choice in choices):
                choices = [(choice, None) for choice in choices]

            self.choices = collections.OrderedDict(choices)
        else:
            self.choices = None

        invalid_choices = [c for c in self.choices or []
                           if (min is not None and min > c)
                           or (max is not None and max < c)]
        if invalid_choices:
            raise ValueError("Choices %s are out of bounds [%s..%s]"
                             % (invalid_choices, min, max))

        self.min = min
        self.max = max
        self.num_type = num_type

    def __call__(self, value):
        if not isinstance(value, self.num_type):
            s = str(value).strip()
            if s == '':
                return None
            value = self.num_type(value)

        if self.choices is None:
            if self.min is not None and value < self.min:
                raise ValueError('Should be greater than or equal to %g' %
                                 self.min)
            if self.max is not None and value > self.max:
                raise ValueError('Should be less than or equal to %g' %
                                 self.max)
        else:
            if value not in self.choices:
                raise ValueError('Valid values are %r, but found %g' % (
                                 self.choices, value))
        return value

    def __repr__(self):
        props = []
        if self.choices is not None:
            props.append("choices={!r}".format(list(self.choices.keys())))
        else:
            if self.min is not None:
                props.append('min=%g' % self.min)
            if self.max is not None:
                props.append('max=%g' % self.max)

        if props:
            return self.__class__.__name__ + '(%s)' % ', '.join(props)
        return self.__class__.__name__

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (self.min == other.min) and
            (self.max == other.max) and
            (set([x for x in self.choices or []]) ==
                set([x for x in other.choices or []]) if
             self.choices and other.choices else
             self.choices == other.choices)
        )

    def _formatter(self, value):
        return str(value)


class Integer(Number):

    """Integer type.

    Converts value to an integer optionally doing range checking.
    If value is whitespace or empty string will return None.

    :param min: Optional check that value is greater than or equal to min.
    :param max: Optional check that value is less than or equal to max.
    :param type_name: Type name to be used in the sample config file.
    :param choices: Optional sequence of either valid values or tuples of valid
        values with descriptions.

    .. versionchanged:: 2.4
       The class now honors zero for *min* and *max* parameters.

    .. versionchanged:: 2.7
       Added *type_name* parameter.

    .. versionchanged:: 3.2
       Added *choices* parameter.

    .. versionchanged:: 3.16
       *choices* is no longer mutually exclusive with *min*/*max*. If those are
       supplied, all choices are verified to be within the range.

    .. versionchanged:: 5.2
       The *choices* parameter will now accept a sequence of tuples, where each
       tuple is of form (*choice*, *description*)
    """

    def __init__(self, min=None, max=None, type_name='integer value',
                 choices=None):
        super(Integer, self).__init__(int, type_name, min=min, max=max,
                                      choices=choices)


class Float(Number):

    """Float type.

    :param min: Optional check that value is greater than or equal to min.
    :param max: Optional check that value is less than or equal to max.
    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.7

       Added *type_name* parameter.

    .. versionchanged:: 3.14

       Added *min* and *max* parameters. If *choices* are also supplied, they
       must be within the range.
    """

    def __init__(self, min=None, max=None, type_name='floating point value'):
        super(Float, self).__init__(float, type_name, min=min, max=max)


class Port(Integer):

    """Port type

    Represents a L4 Port.

    :param min: Optional check that value is greater than or equal to min.
    :param max: Optional check that value is less than or equal to max.
    :param type_name: Type name to be used in the sample config file.
    :param choices: Optional sequence of either valid values or tuples of valid
        values with descriptions.

    .. versionadded:: 3.16

    .. versionchanged:: 5.2
       The *choices* parameter will now accept a sequence of tuples, where each
       tuple is of form (*choice*, *description*)
    """

    PORT_MIN = 0
    PORT_MAX = 65535

    def __init__(self, min=None, max=None, type_name='port', choices=None):
        min = self.PORT_MIN if min is None else min
        max = self.PORT_MAX if max is None else max
        if min < self.PORT_MIN:
            raise ValueError('Min value cannot be less than %(min)d' %
                             {'min': self.PORT_MIN})
        if max > self.PORT_MAX:
            raise ValueError('Max value cannot be more than %(max)d' %
                             {'max': self.PORT_MAX})

        super(Port, self).__init__(min=min, max=max, type_name=type_name,
                                   choices=choices)


class List(ConfigType):

    """List type.

    Represent values of other (item) type, separated by commas.
    The resulting value is a list containing those values.

    List doesn't know if item type can also contain commas. To workaround this
    it tries the following: if the next part fails item validation, it appends
    comma and next item until validation succeeds or there is no parts left.
    In the later case it will signal validation error.

    :param item_type: Type of list items. Should be an instance of
                      ``ConfigType``.
    :param bounds: if True, value should be inside "[" and "]" pair
    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.7

       Added *type_name* parameter.
    """

    def __init__(self, item_type=None, bounds=False, type_name='list value'):
        super(List, self).__init__(type_name=type_name)

        if item_type is None:
            item_type = String()

        if not callable(item_type):
            raise TypeError('item_type must be callable')
        self.item_type = item_type
        self.bounds = bounds

    def __call__(self, value):
        if isinstance(value, (list, tuple)):
            return list(map(self.item_type, value))

        s = value.strip().rstrip(',')
        if self.bounds:
            if not s.startswith('['):
                raise ValueError('Value should start with "["')
            if not s.endswith(']'):
                raise ValueError('Value should end with "]"')
            s = s[1:-1]
        if s:
            values = s.split(',')
        else:
            values = []
        if not values:
            return []

        result = []
        while values:
            value = values.pop(0)
            while True:
                first_error = None
                try:
                    validated_value = self.item_type(value.strip())
                    break
                except ValueError as e:
                    if not first_error:
                        first_error = e
                    if len(values) == 0:
                        raise first_error

                value += ',' + values.pop(0)

            result.append(validated_value)

        return result

    def __repr__(self):
        return 'List of %s' % repr(self.item_type)

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (self.item_type == other.item_type)
        )

    def _formatter(self, value):
        fmtstr = '[{}]' if self.bounds else '{}'
        if isinstance(value, str):
            return fmtstr.format(value)
        if isinstance(value, list):
            value = [
                self.item_type._formatter(v)
                for v in value
            ]
            return fmtstr.format(','.join(value))
        return fmtstr.format(self.item_type._formatter(value))


class Range(ConfigType):

    """Range type.

    Represents a range of integers. A range is identified by an integer both
    sides of a '-' character. Negatives are allowed. A single number is also a
    valid range.

    :param min: Optional check that lower bound is greater than or equal to
                min.
    :param max: Optional check that upper bound is less than or equal to max.
    :param inclusive: True if the right bound is to be included in the range.
    :param type_name: Type name to be used in the sample config file.

    .. versionadded:: 3.18
    """

    def __init__(self, min=None, max=None, inclusive=True,
                 type_name='range value'):
        super(Range, self).__init__(type_name)
        self.min = min
        self.max = max
        self.inclusive = inclusive

    def __call__(self, value):
        value = str(value)
        num = "0|-?[1-9][0-9]*"
        m = re.match("^(%s)(?:-(%s))?$" % (num, num), value)
        if not m:
            raise ValueError('Invalid Range: %s' % value)
        left = int(m.group(1))
        right = int(left if m.group(2) is None else m.group(2))

        if left < right:
            left = Integer(min=self.min)(left)
            right = Integer(max=self.max)(right)
            step = 1
        else:
            left = Integer(max=self.max)(left)
            right = Integer(min=self.min)(right)
            step = -1
        if self.inclusive:
            right += step
        return range(left, right, step)

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (self.min == other.min) and
            (self.max == other.max)
        )

    def _formatter(self, value):
        return value


class Dict(ConfigType):

    """Dictionary type.

    Dictionary type values are key:value pairs separated by commas.
    The resulting value is a dictionary of these key/value pairs.
    Type of dictionary key is always string, but dictionary value
    type can be customized.

    :param value_type: type of values in dictionary
    :param bounds: if True, value should be inside "{" and "}" pair
    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.7

       Added *type_name* parameter.
    """

    def __init__(self, value_type=None, bounds=False, type_name='dict value'):
        super(Dict, self).__init__(type_name=type_name)

        if value_type is None:
            value_type = String()

        if not callable(value_type):
            raise TypeError('value_type must be callable')
        self.value_type = value_type
        self.bounds = bounds

    def __call__(self, value):
        if isinstance(value, dict):
            return value

        result = {}
        s = value.strip()

        if self.bounds:
            if not s.startswith('{'):
                raise ValueError('Value should start with "{"')
            if not s.endswith('}'):
                raise ValueError('Value should end with "}"')
            s = s[1:-1]

        if s == '':
            return result

        pairs = s.split(',')
        while pairs:
            pair = pairs.pop(0)

            while True:
                first_error = None
                try:
                    key_value = pair.split(':', 1)

                    if len(key_value) < 2:
                        raise ValueError('Value should be NAME:VALUE pairs '
                                         'separated by ","')

                    key, value = key_value
                    key = key.strip()
                    value = value.strip()

                    value = self.value_type(value)
                    break
                except ValueError as e:
                    if not first_error:
                        first_error = e
                    if not pairs:
                        raise first_error

                pair += ',' + pairs.pop(0)

            if key == '':
                raise ValueError('Key name should not be empty')

            if key in result:
                raise ValueError('Duplicate key %s' % key)

            result[key] = value

        return result

    def __repr__(self):
        return 'Dict of %s' % repr(self.value_type)

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (self.value_type == other.value_type)
        )

    def _formatter(self, value):
        sorted_items = sorted(value.items(),
                              key=operator.itemgetter(0))
        return ','.join(['%s:%s' % i for i in sorted_items])


class IPAddress(ConfigType):

    """IP address type

    Represents either ipv4 or ipv6. Without specifying version parameter both
    versions are checked

    :param version: defines which version should be explicitly checked (4 or 6)
    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.7

       Added *type_name* parameter.
    """

    def __init__(self, version=None, type_name='IP address value'):
        super(IPAddress, self).__init__(type_name=type_name)
        version_checkers = {
            None: self._check_both_versions,
            4: self._check_ipv4,
            6: self._check_ipv6
        }

        self.version_checker = version_checkers.get(version)
        if self.version_checker is None:
            raise TypeError("%s is not a valid IP version." % version)

    def __call__(self, value):
        value = str(value)
        if not value:
            raise ValueError("IP address cannot be an empty string")
        self.version_checker(value)
        return value

    def __repr__(self):
        return "IPAddress"

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def _check_ipv4(self, address):
        if not netaddr.valid_ipv4(address, netaddr.core.INET_PTON):
            raise ValueError("%s is not an IPv4 address" % address)

    def _check_ipv6(self, address):
        if not netaddr.valid_ipv6(address, netaddr.core.INET_PTON):
            raise ValueError("%s is not an IPv6 address" % address)

    def _check_both_versions(self, address):
        if not (netaddr.valid_ipv4(address, netaddr.core.INET_PTON) or
                netaddr.valid_ipv6(address, netaddr.core.INET_PTON)):
            raise ValueError("%s is not IPv4 or IPv6 address" % address)

    def _formatter(self, value):
        return value


class Hostname(ConfigType):
    """Host domain name type.

    A hostname refers to a valid DNS or hostname. It must not be longer than
    253 characters, have a segment greater than 63 characters, nor start or
    end with a hyphen.

    :param type_name: Type name to be used in the sample config file.

    """

    def __init__(self, type_name='hostname value'):
        super(Hostname, self).__init__(type_name=type_name)

    def __call__(self, value):
        """Check hostname is valid.

        Ensures that each segment
        - Contains at least one character and a maximum of 63 characters
        - Consists only of allowed characters: letters (A-Z and a-z),
          digits (0-9), and hyphen (-)
        - Ensures that the final segment (representing the top level domain
          name) contains at least one non-numeric character
        - Does not begin or end with a hyphen
        - maximum total length of 253 characters

        For more details , please see: http://tools.ietf.org/html/rfc1035,
        https://www.ietf.org/rfc/rfc1912, and
        https://tools.ietf.org/html/rfc1123
        """

        if len(value) == 0:
            raise ValueError("Cannot have an empty hostname")
        if len(value) > 253:
            raise ValueError("hostname is greater than 253 characters: %s"
                             % value)
        if value.endswith("."):
            value = value[:-1]
        allowed = re.compile("(?!-)[A-Z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
        if not re.search('[a-zA-Z-]', value.split(".")[-1]):
            raise ValueError('%s contains no non-numeric characters in the '
                             'top-level domain part of the host name and is '
                             'invalid' % value)
        if any((not allowed.match(x)) for x in value.split(".")):
            raise ValueError("%s is an invalid hostname" % value)
        return value

    def __repr__(self):
        return 'Hostname'

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def _formatter(self, value):
        return value


class HostAddress(ConfigType):
    """Host Address type.

    Represents both valid IP addresses and valid host domain names
    including fully qualified domain names.
    Performs strict checks for both IP addresses and valid hostnames,
    matching the opt values to the respective types as per RFC1912.

    :param version: defines which version should be explicitly
                    checked (4 or 6) in case of an IP address
    :param type_name: Type name to be used in the sample config file.
    """

    def __init__(self, version=None, type_name='host address value'):
        """Check for valid version in case an IP address is provided

        """

        super(HostAddress, self).__init__(type_name=type_name)
        self.ip_address = IPAddress(version, type_name)
        self.hostname = Hostname('localhost')

    def __call__(self, value):
        """Checks if is a valid IP/hostname.

        If not a valid IP, makes sure it is not a mistyped IP before
        performing checks for it as a hostname.

        """

        try:
            value = self.ip_address(value)
        except ValueError:
            try:
                value = self.hostname(value)
            except ValueError:
                raise ValueError("%s is not a valid host address" % (value,))
        return value

    def __repr__(self):
        return 'HostAddress'

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def _formatter(self, value):
        return value


class URI(ConfigType):

    """URI type

    Represents URI. Value will be validated as RFC 3986.

    :param max_length: Optional integer. If a positive value is specified,
                       a maximum length of an option value must be less than
                       or equal to this parameter. Otherwise no length check
                       will be done.
    :param schemes: List of valid schemes.
    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 3.14
       Added *max_length* parameter.
    .. versionchanged:: 3.18
       Added *schemes* parameter.
    """

    def __init__(self, max_length=None, schemes=None, type_name='uri value'):
        super(URI, self).__init__(type_name=type_name)
        self.max_length = max_length
        self.schemes = schemes

    def __call__(self, value):
        uri = rfc3986.uri_reference(value)
        validator = rfc3986.validators.Validator().require_presence_of(
            'scheme', 'host',
        ).check_validity_of(
            'scheme', 'host', 'path',
        )
        if self.schemes:
            validator = validator.allow_schemes(*self.schemes)
        try:
            validator.validate(uri)
        except rfc3986.exceptions.RFC3986Exception as exc:
            raise ValueError(exc)

        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError("Value '%s' exceeds maximum length %d" %
                             (value, self.max_length))

        # NOTE(dhellmann): self.value is deprecated, and we don't want
        # to trigger a deprecation warning ourselves so we modify
        # self._value directly.
        self._value = value
        return value

    @removals.removed_property
    def value(self):
        return self._value

    @value.setter
    def value(self, newval):
        self._value = newval

    @value.deleter
    def value(self):
        del self._value

    def __repr__(self):
        return 'URI'

    def __eq__(self, other):
        to_compare = ['__class__', 'max_length', 'schemes']
        unset = object()
        my_values = tuple(
            getattr(self, name, unset) for name in to_compare
        )
        other_values = tuple(
            getattr(other, name, unset) for name in to_compare
        )
        return my_values == other_values

    def _formatter(self, value):
        return value
