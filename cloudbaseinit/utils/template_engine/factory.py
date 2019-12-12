# Copyright 2019 Cloudbase Solutions Srl
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

import re

from oslo_log import log as oslo_logging

from cloudbaseinit.utils import classloader

TEMPLATE_CLASS_PATHS = {
    "jinja": "cloudbaseinit.utils.template_engine.jinja2.Jinja2TemplateEngine"
}
LOG = oslo_logging.getLogger(__name__)


def get_template_manager(userdata):
    """Returns the template manager depending on the userdata header"""

    try:
        template_matcher = re.compile(r"##\s*template:(.*)", re.I)
        template_engine_match = template_matcher.match(userdata.decode())

        if template_engine_match:
            template_engine = template_engine_match.group(1).lower().strip()
            if TEMPLATE_CLASS_PATHS.get(template_engine, None):
                cl = classloader.ClassLoader()
                return cl.load_class(TEMPLATE_CLASS_PATHS[template_engine])()
            else:
                LOG.info("Template engine '%s' is not supported."
                         % template_engine)
    except Exception:
        LOG.debug("Could not load userdata template manager.")
        raise
