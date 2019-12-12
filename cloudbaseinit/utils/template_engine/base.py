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

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseTemplateEngine(object):
    @abc.abstractmethod
    def render(self, data, template):
        """Renders the template according to the data dictionary

        The data variable is a dict which contains the key-values
        that will be used to render the template.

        The template is an encoded string which can contain special
        constructions that will be used by the template engine.

        The return value will be an encoded string.
        """
        pass
