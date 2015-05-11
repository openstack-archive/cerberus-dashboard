#
#   Copyright (c) 2015 EUROGICIEL
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

from django.utils.translation import ugettext_lazy as _
from horizon import tables


class PluginsTable(tables.DataTable):
    uuid = tables.Column("uuid",
                         link=("horizon:security:plugins:details"),
                         verbose_name="uuid",)
    name = tables.Column("name", verbose_name=_("Name"))
    version = tables.Column("version", verbose_name=_("Version"))
    provider = tables.Column("provider", verbose_name=_("Provider"))
    type = tables.Column("type", verbose_name=_("Type"))
    description = tables.Column("description", verbose_name=_("Description"),
                                truncate=30)
    tool_name = tables.Column("tool_name", verbose_name=_("Tool name"))

    def get_object_id(self, datum):
        return datum.uuid

    class Meta:
        name = "plugins"
        verbose_name = _("Plugins")
