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

import datetime
import logging

import iso8601
import six


def get_logger(name):
    name = name.replace(__name__.split('.')[0], 'keystoneauth')
    return logging.getLogger(name)


logger = get_logger(__name__)


def normalize_time(timestamp):
    """Normalize time in arbitrary timezone to UTC naive object."""
    offset = timestamp.utcoffset()
    if offset is None:
        return timestamp
    return timestamp.replace(tzinfo=None) - offset


def parse_isotime(timestr):
    """Parse time from ISO 8601 format."""
    try:
        return iso8601.parse_date(timestr)
    except iso8601.ParseError as e:
        raise ValueError(six.text_type(e))
    except TypeError as e:
        raise ValueError(six.text_type(e))


def from_utcnow(**timedelta_kwargs):
    r"""Calculate the time in the future from utcnow.

    :param \*\*timedelta_kwargs:
        Passed directly to :class:`datetime.timedelta` to add to the current
        time in UTC.
    :returns:
        The time in the future based on ``timedelta_kwargs``.
    :rtype:
        datetime.datetime
    """
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(**timedelta_kwargs)
    return now + delta


def before_utcnow(**timedelta_kwargs):
    r"""Calculate the time in the past from utcnow.

    :param \*\*timedelta_kwargs:
        Passed directly to :class:`datetime.timedelta` to subtract from the
        current time in UTC.
    :returns:
        The time in the past based on ``timedelta_kwargs``.
    :rtype:
        datetime.datetime
    """
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(**timedelta_kwargs)
    return now - delta


# Detect if running on the Windows Subsystem for Linux
try:
    with open('/proc/version', 'r') as f:
        is_windows_linux_subsystem = 'microsoft' in f.read().lower()
except IOError:
    is_windows_linux_subsystem = False
