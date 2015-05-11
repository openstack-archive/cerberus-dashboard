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
from cerberusdashboard.security_reports import tables as s_tables
from cerberusdashboard.security_reports import tabs as s_tabs


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = s_tables.SecurityReportsTable
    template_name = 'security_reports/index.html'

    def get_data(self):
        try:
            security_reports = cerberus.security_report_list(self.request)
        except Exception:
            raise
        return security_reports


class DetailView(tabs.TabbedTableView):
    tab_group_class = s_tabs.DetailsTabs
    template_name = 'security_reports/detail.html'
    redirect_url = 'horizon/security/security_reports:index'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["security_report"] = self.get_data()
        return context

    def get_data(self):
        report_id = self.kwargs['report_id']
        try:
            security_report = cerberus.security_report_get(
                self.request, report_id)
        except Exception as e:
            LOG.exception(e)
            redirect = reverse_lazy(self.redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'security report "%s".') % report_id,
                              redirect=redirect)
            # Not all exception types handled above will result in a redirect.
            # Need to raise here just in case.
            raise exceptions.Http302(redirect)

        return security_report

    def get_tabs(self, request, *args, **kwargs):
        security_report = self.get_data()
        return self.tab_group_class(request,
                                    security_report=security_report,
                                    **kwargs)
