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

import six

from datetime import datetime
from oslo_log import log as oslo_logging

from cloudbaseinit import conf as cloudbaseinit_conf
from cloudbaseinit import exception
from cloudbaseinit.osutils import factory as osutils_factory
from cloudbaseinit.plugins.common.userdataplugins.cloudconfigplugins import (
    base
)

CONF = cloudbaseinit_conf.CONF
LOG = oslo_logging.getLogger(__name__)


class UsersPlugin(base.BaseCloudConfigPlugin):
    """Creates users given in the cloud-config format."""

    def _get_groups(self, data):
        """Retuns all the group names that the user should be added to.

        :rtype: list
        """
        groups = data.get('groups', None)
        primary_group = data.get('primary-group', None)
        user_groups = []
        if isinstance(groups, six.string_types):
                user_groups.extend(groups.split(', '))
        elif isinstance(groups, (list, tuple)):
                user_groups.extend(groups)
        if isinstance(primary_group, six.string_types):
                user_groups.extend(primary_group.split(', '))
        elif isinstance(primary_group, (list, tuple)):
                user_groups.extend(primary_group)
        return user_groups

    def _get_password(self, data, osutils):
        password = data.get('passwd', None)
        max_size = osutils.get_maximum_password_length()
        if password is not None and len(password) > max_size:
            password = password[:max_size]
            LOG.warning("New password has been sliced to %s characters",
                        max_size)
        return password

    def _get_expire_status(self, data):
        expiredate = data.get('expiredate', None)
        if not expiredate:
            return False
        if isinstance(expiredate, six.string_types):
            year, month, day = map(int, expiredate.split('-'))
            expiredate = datetime(year=year, month=month, day=day).date()
        current_date = datetime.now().date()
        return False if expiredate <= current_date else True

    def _get_user_activity(self, data):
        activity = data.get('inactive', None)
        if not activity:
            return False
        return True if activity.lower() == "true" else False

    @staticmethod
    def _create_user_logon(user_name, password, password_expires, osutils):
        try:
            # Create a user profile in order for other plugins
            # to access the user home, etc
            token = osutils.create_user_logon_session(user_name,
                                                      password,
                                                      password_expires)
            osutils.close_user_logon_session(token)
        except Exception:
            LOG.exception('Cannot create a user logon session for user: "%s"',
                          user_name)

    def _create_user(self, item, osutils):
            user_name = item.get('name', None)
            user_description = item.get('gecos', None)
            password = self._get_password(item, osutils)
            password_expires = self._get_expire_status(item)
            groups = self._get_groups(item)

            if osutils.user_exists(user_name):
                LOG.warning("User '%s' already exists " % user_name)
                if password is not None:
                    osutils.set_user_password(user_name, password,
                                              password_expires)
            else:
                if password is None:
                    password = osutils.generate_random_password(
                        CONF.user_password_length)
                osutils.create_user(user_name, password,
                                    description=user_description)
                self._create_user_logon(user_name, password,
                                        password_expires, osutils)

            for group in groups:
                try:
                    osutils.add_user_to_local_group(user_name, group)
                except Exception:
                    LOG.exception('Cannot add user "%s" to group "%s"' %
                                  (user_name, group))

    def process(self, data):
        """Process the given data received from the cloud-config userdata.

        It knows to process only lists and dicts.
        """
        if not isinstance(data, (list, dict)):
            raise exception.CloudbaseInitException(
                "Can't process the type of data %r" % type(data))

        osutils = osutils_factory.get_os_utils()
        for item in data:
            if not isinstance(item, dict):
                continue
            if not {'name'}.issubset(set(item)):
                LOG.warning("Missing required keys from file information %s",
                            item)
                continue
            user_name = item.get('name', None)
            if not user_name:
                LOG.warning("Username cannot be empty")
                continue

            try:
                self._create_user(item, osutils)
            except Exception as ex:
                LOG.warning("An error occurred during user '%s' creation: '%s"
                            % user_name, ex)

        return False
