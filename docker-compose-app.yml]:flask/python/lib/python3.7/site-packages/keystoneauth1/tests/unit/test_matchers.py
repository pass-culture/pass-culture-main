# Copyright 2013 OpenStack Foundation
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

import testtools
from testtools import matchers as tt_matchers

from keystoneauth1.tests.unit import matchers as ks_matchers

# NOTE(jamielennox): The tests in this file are copied form the non-public
# testtools.tests.matchers.helpers.TestMatchersInterface.


class TestXMLEquals(testtools.TestCase):
    matches_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<test xmlns="https://docs.openstack.org/identity/api/v2.0">
    <first z="0" y="1" x="2"/>
    <second a="a" b="b"></second>
</test>
"""
    equivalent_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<test xmlns="https://docs.openstack.org/identity/api/v2.0">
    <second a="a" b="b"/>
    <first z="0" y="1" x="2"></first>
</test>
"""
    mismatches_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<test xmlns="https://docs.openstack.org/identity/api/v2.0">
    <nope_it_fails/>
</test>
"""
    mismatches_description = """expected =
<test xmlns="https://docs.openstack.org/identity/api/v2.0">
  <first z="0" y="1" x="2"/>
  <second a="a" b="b"/>
</test>

actual =
<test xmlns="https://docs.openstack.org/identity/api/v2.0">
  <nope_it_fails/>
</test>
"""

    matches_matcher = ks_matchers.XMLEquals(matches_xml)
    matches_matches = [matches_xml, equivalent_xml]
    matches_mismatches = [mismatches_xml]
    describe_examples = [
        (mismatches_description, mismatches_xml, matches_matcher),
    ]
    str_examples = [('XMLEquals(%r)' % matches_xml, matches_matcher)]

    def test_matches_match(self):
        matcher = self.matches_matcher
        matches = self.matches_matches
        mismatches = self.matches_mismatches
        for candidate in matches:
            self.assertIsNone(matcher.match(candidate))
        for candidate in mismatches:
            mismatch = matcher.match(candidate)
            self.assertIsNotNone(mismatch)
            self.assertIsNotNone(getattr(mismatch, 'describe', None))

    def test__str__(self):
        # [(expected, object to __str__)].
        examples = self.str_examples
        for expected, matcher in examples:
            self.assertThat(matcher, tt_matchers.DocTestMatches(expected))

    def test_describe_difference(self):
        # [(expected, matchee, matcher), ...]
        examples = self.describe_examples
        for difference, matchee, matcher in examples:
            mismatch = matcher.match(matchee)
            self.assertEqual(difference, mismatch.describe())

    def test_mismatch_details(self):
        # The mismatch object must provide get_details, which must return a
        # dictionary mapping names to Content objects.
        examples = self.describe_examples
        for difference, matchee, matcher in examples:
            mismatch = matcher.match(matchee)
            details = mismatch.get_details()
            self.assertEqual(dict(details), details)
