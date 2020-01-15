# Copyright 2020 Cloudbase Solutions Srl
# Copyright 2019 ruilopes.com
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

import base64
import gzip
import io
import json
import os
import yaml
from oslo_log import log as oslo_logging

from cloudbaseinit import conf as cloudbaseinit_conf
from cloudbaseinit import exception
from cloudbaseinit.metadata.services import base
from cloudbaseinit.osutils import factory as osutils_factory

CONF = cloudbaseinit_conf.CONF
LOG = oslo_logging.getLogger(__name__)


class VMwareGuestService(base.BaseMetadataService):
    def __init__(self):
        super(VMwareGuestService, self).__init__()
        self._rpc_tool_path = None
        self._osutils = osutils_factory.get_os_utils()

    def load(self):
        super(VMwareGuestService, self).load()

        if not CONF.vmwareguest.vmware_rpctool_path:
            LOG.info("rpctool_path is empty. "
                     "Please provide a value for VMware rpctool path.")
            return False

        self._rpc_tool_path = os.path.abspath(
            os.path.expandvars(CONF.vmwareguest.vmware_rpctool_path))

        if not os.path.exists(self._rpc_tool_path):
            LOG.info("%s does not exist. "
                     "Please provide a valid value for VMware rpctool path."
                     % self._rpc_tool_path)
            return False

        try:
            self._meta_data = yaml.load(
                self._get_guestinfo_value('metadata')) or {}
        except exception.CloudbaseInitException as exc:
            LOG.exception(exc)
            return False

        return True

    def _get_guestinfo_value(self, key):
        stdout, stderr, exit_code = self._osutils.execute_process([
            self._rpc_tool_path,
            'info-get guestinfo.%s' % key
        ])
        if exit_code:
            raise exception.CloudbaseInitException(
                'Failed to execute "%(rpctool_path)s" with '
                'exit code: %(exit_code)s\nstdout: '
                '%(stdout)s\nstderr: %(stderr)s' % {
                    'rpctool_path': self._rpc_tool_path,
                    'exit_code': exit_code,
                    'stdout': stdout,
                    'stderr': stderr})
        data = base64.b64decode(stdout)
        if data[:2] == self._GZIP_MAGIC_NUMBER:
            with gzip.GzipFile(fileobj=io.BytesIO(data), mode='rb') as out:
                data = out.read()
        return data

    def _get_data(self, path):
        pass

    def get_user_data(self):
        return self._get_guestinfo_value('userdata')

    def get_host_name(self):
        return self._meta_data.get('local-hostname')

    def get_public_keys(self):
        return self._meta_data.get('public-keys')

    def get_admin_username(self):
        return self._meta_data.get('admin-username')

    def get_admin_password(self):
        return self._meta_data.get('admin-password')
