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
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import logging

from horizon import exceptions
from horizon import tables
from horizon import tabs

from cerberusdashboard import api
from cerberusdashboard.tasks import tables as t_tables
from cerberusdashboard.tasks import tabs as t_tabs


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = t_tables.TasksTable
    template_name = 'tasks/index.html'

    def get_data(self):
        try:
            tasks = api.cerberus.task_list(self.request)
        except Exception:
            raise
        return tasks


class DetailView(tabs.TabbedTableView):
    tab_group_class = t_tabs.DetailsTabs
    template_name = 'tasks/detail.html'
    redirect_url = 'horizon:security:tasks:index'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["task"] = self.get_data()
        return context

    def get_data(self):
        id = self.kwargs['id']
        try:
            task = api.cerberus.task_get(self.request, id)
        except Exception as e:
            LOG.exception(e)
            redirect = reverse(self.redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'task "%s".') % id,
                              redirect=redirect)
            # Not all exception types handled above will result in a redirect.
            # Need to raise here just in case.
            raise exceptions.Http302(redirect)

        return task

    def get_tabs(self, request, *args, **kwargs):
        task = self.get_data()
        return self.tab_group_class(request, task=task, **kwargs)
