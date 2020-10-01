# -*- coding: utf-8 -*-

#    Copyright (C) 2015 Yahoo! Inc. All Rights Reserved.
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

import fixtures

from debtcollector import _utils


class DisableFixture(fixtures.Fixture):
    """Fixture that disables debtcollector triggered warnings.

    This does **not** disable warnings calls emitted by other libraries.

    This can be used like::

        from debtcollector.fixtures import disable

        with disable.DisableFixture():
            <some code that calls into depreciated code>
    """

    def _setUp(self):
        self.addCleanup(setattr, _utils, "_enabled", True)
        _utils._enabled = False
