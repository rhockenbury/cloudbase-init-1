# Copyright 2016 Cloudbase Solutions Srl
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

import unittest

try:
    import unittest.mock as mock
except ImportError:
    import mock
from oslo_config import cfg

from cloudbaseinit import exception
from cloudbaseinit.plugins.common.userdataplugins.cloudconfigplugins import (
    groups
)
from cloudbaseinit.tests import testutils

CONF = cfg.CONF
MODPATH = ("cloudbaseinit.plugins.common.userdataplugins."
           "cloudconfigplugins.groups")


class GroupsPluginTests(unittest.TestCase):

    def setUp(self):
        self.groups_plugin = groups.GroupsPlugin()

    def test_process_user_empty(self):
        fake_data = ['']
        with testutils.LogSnatcher(MODPATH) as snatcher:
            res = self.groups_plugin.process(fake_data)
        self.assertEqual(['Group name cannot be empty'], snatcher.output)

    def test_process_user(self):
        fake_data = [{'test1': ['tt', 'bt']}]
        with testutils.LogSnatcher(MODPATH) as snatcher:
            res = self.groups_plugin.process(fake_data)
        self.assertEqual(['Group name cannot be empty'], snatcher.output)
