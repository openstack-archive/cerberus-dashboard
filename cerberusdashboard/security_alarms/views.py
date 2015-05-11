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

import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon import tabs

from cerberusdashboard.api import cerberus
from cerberusdashboard.security_alarms import tables as s_tables
from cerberusdashboard.security_alarms import tabs as s_tabs


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = s_tables.SecurityAlarmsTable
    template_name = 'security_alarms/index.html'

    def get_data(self):
        try:
            security_alarms = cerberus.security_alarm_list(self.request)
        except Exception:
            raise
        return security_alarms


class DetailView(tabs.TabbedTableView):
    tab_group_class = s_tabs.DetailsTabs
    template_name = 'security_alarms/detail.html'
    redirect_url = 'security_alarms:index'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["security_alarm"] = self.get_data()
        return context

    def get_data(self):
        alarm_id = self.kwargs['alarm_id']
        try:
            security_alarm = cerberus.security_alarm_get(
                self.request, alarm_id)
        except Exception as e:
            LOG.exception(e)
            redirect = reverse_lazy(self.redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'security alarm "%s".') % alarm_id,
                              redirect=redirect)
            # Not all exception types handled above will result in a redirect.
            # Need to raise here just in case.
            raise exceptions.Http302(redirect)

        return security_alarm

    def get_tabs(self, request, *args, **kwargs):
        security_alarm = self.get_data()
        return self.tab_group_class(request,
                                    security_alarm=security_alarm,
                                    **kwargs)
