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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
import logging

from horizon import exceptions
from horizon import tables
from horizon import tabs

from cerberusdashboard import api
from cerberusdashboard.plugins import tables as p_tables
from cerberusdashboard.plugins import tabs as p_tabs


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = p_tables.PluginsTable
    template_name = 'plugins/index.html'

    @staticmethod
    def get_redirect_url():
        return reverse_lazy('horizon:security:plugins:index')

    def get_data(self):
        try:
            plugins = api.cerberus.plugin_list(self.request)
        except Exception as e:
            LOG.exception(e)
            exceptions.handle(self.request,
                              _('Unable to retrieve plugins details.'),
                              redirect=self.get_redirect_url())
        return plugins


class DetailView(tabs.TabView):
    tab_group_class = p_tabs.PluginDetailTabs
    template_name = 'plugins/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        plugin = self.get_data()
        context["plugin"] = plugin
        return context

    def get_data(self):
        try:
            return api.cerberus.plugin_get(self.request,
                                           self.kwargs['plugin_id'])
        except Exception as e:
            LOG.exception(e)
            exceptions.handle(self.request,
                              _('Unable to retrieve plugin details.'),
                              redirect=self.get_redirect_url())

    @staticmethod
    def get_redirect_url():
        return reverse_lazy('horizon:security:plugins:index')

    def get_tabs(self, request, *args, **kwargs):
        plugin = self.get_data()
        return self.tab_group_class(request, plugin=plugin, **kwargs)
