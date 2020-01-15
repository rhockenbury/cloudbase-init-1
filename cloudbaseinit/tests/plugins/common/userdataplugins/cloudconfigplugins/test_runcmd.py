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

from cloudbaseinit.plugins.common.userdataplugins.cloudconfigplugins import (
    runcmd
)

from cloudbaseinit.tests import testutils

CONF = cfg.CONF


class RunCmdPluginTest(unittest.TestCase):

    def setUp(self):
        self._runcmd_plugin = runcmd.RunCmdPlugin()

    @mock.patch('cloudbaseinit.plugins.common.'
                'userdatautils.execute_user_data_script')
    @mock.patch('cloudbaseinit.osutils.factory.get_os_utils')
    def test_process_basic_data(self, mock_os_utils, mock_userdata):
        run_commands = ['echo 1', 'echo 2', ['echo', '1'], 'exit 1003']
        mock_os_util = mock.MagicMock()
        mock_os_util.get_execution_environment_header.return_value = "test"
        mock_os_utils.return_value = mock_os_util
        mock_userdata.return_value = 1003
        expected_logging = [
            "Running cloud-config runcmd entries.",
            "Found 4 cloud-config runcmd entries.",
        ]
        with testutils.LogSnatcher('cloudbaseinit.plugins.common.'
                                   'userdataplugins.cloudconfigplugins.'
                                   'runcmd') as snatcher:
            result_process = self._runcmd_plugin.process(run_commands)
        self.assertEqual(expected_logging, snatcher.output)
        self.assertEqual(result_process, True)
