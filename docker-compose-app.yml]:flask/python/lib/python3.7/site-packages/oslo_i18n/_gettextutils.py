# Copyright 2012 Red Hat, Inc.
# Copyright 2013 IBM Corp.
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

"""gettextutils provides a wrapper around gettext for OpenStack projects
"""

import copy
import gettext
import locale
import os

from oslo_i18n import _factory
from oslo_i18n import _locale

__all__ = [
    'install',
    'get_available_languages',
]


def install(domain):
    """Install a _() function using the given translation domain.

    Given a translation domain, install a _() function using gettext's
    install() function.

    The main difference from gettext.install() is that we allow
    overriding the default localedir (e.g. /usr/share/locale) using
    a translation-domain-specific environment variable (e.g.
    NOVA_LOCALEDIR).

    :param domain: the translation domain
    """
    from six import moves
    tf = _factory.TranslatorFactory(domain)
    moves.builtins.__dict__['_'] = tf.primary


_AVAILABLE_LANGUAGES = {}
# Copied from Babel so anyone using aliases that were previously provided by
# the Babel implementation of get_available_languages continues to work. These
# are not recommended for use in new code.
_BABEL_ALIASES = {
    'ar': 'ar_SY', 'bg': 'bg_BG', 'bs': 'bs_BA', 'ca': 'ca_ES', 'cs': 'cs_CZ',
    'da': 'da_DK', 'de': 'de_DE', 'el': 'el_GR', 'en': 'en_US', 'es': 'es_ES',
    'et': 'et_EE', 'fa': 'fa_IR', 'fi': 'fi_FI', 'fr': 'fr_FR', 'gl': 'gl_ES',
    'he': 'he_IL', 'hu': 'hu_HU', 'id': 'id_ID', 'is': 'is_IS', 'it': 'it_IT',
    'ja': 'ja_JP', 'km': 'km_KH', 'ko': 'ko_KR', 'lt': 'lt_LT', 'lv': 'lv_LV',
    'mk': 'mk_MK', 'nl': 'nl_NL', 'nn': 'nn_NO', 'no': 'nb_NO', 'pl': 'pl_PL',
    'pt': 'pt_PT', 'ro': 'ro_RO', 'ru': 'ru_RU', 'sk': 'sk_SK', 'sl': 'sl_SI',
    'sv': 'sv_SE', 'th': 'th_TH', 'tr': 'tr_TR', 'uk': 'uk_UA'
}


def get_available_languages(domain):
    """Lists the available languages for the given translation domain.

    :param domain: the domain to get languages for
    """
    if domain in _AVAILABLE_LANGUAGES:
        return copy.copy(_AVAILABLE_LANGUAGES[domain])

    localedir = os.environ.get(_locale.get_locale_dir_variable_name(domain))

    def find(x):
        return gettext.find(domain, localedir=localedir, languages=[x])

    # NOTE(mrodden): en_US should always be available (and first in case
    # order matters) since our in-line message strings are en_US
    language_list = ['en_US']
    locale_identifiers = set(locale.windows_locale.values())
    language_list.extend(
        language for language in locale_identifiers if find(language)
    )
    language_list.extend(
        alias for alias, _ in _BABEL_ALIASES.items() if find(alias)
    )

    _AVAILABLE_LANGUAGES[domain] = language_list
    return copy.copy(language_list)


_original_find = gettext.find
_FIND_CACHE = {}


def cached_find(domain, localedir=None, languages=None, all=0):
    """A version of gettext.find using a cache.

    gettext.find looks for mo files on the disk using os.path.exists. Those
    don't tend to change over time, but the system calls pile up with a
    long-running service. This caches the result so that we return the same mo
    files, and only call find once per domain.
    """
    key = (domain,
           localedir,
           tuple(languages) if languages is not None else None,
           all)
    if key in _FIND_CACHE:
        return _FIND_CACHE[key]
    result = _original_find(domain, localedir, languages, all)
    _FIND_CACHE[key] = result
    return result


gettext.find = cached_find
