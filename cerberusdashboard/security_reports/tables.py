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

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables

from cerberusdashboard import api


LOG = logging.getLogger(__name__)


def is_associated(report):
    ticket_id = getattr(report, "ticket_id", None)
    if not ticket_id:
        return False
    else:
        return True


class CreateTicket(tables.BatchAction):
    name = "create_ticket"
    action_present = _("Create")
    action_past = _("%(data_type)s created")
    data_type_singular = _("Ticket")
    data_type_plural = _("Tickets")
    classes = ('btn-danger', 'btn-terminate')
    failure_url = urlresolvers.reverse_lazy(
        'horizon:security:security_reports:index')

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, 'tenant_id', None)
        return {"project_id": project_id}

    def allowed(self, request, report=None):
        """Allow terminate action if instance not currently being deleted."""
        return not(is_associated(report))

    def action(self, request, report_id):
        report = api.cerberus.security_report_get(request, report_id)
        data = {'project': report.project_id, 'title': report.title}
        try:
            ticket = api.cerberus.ticket_create(request, data)
            api.cerberus.security_report_put_ticket_id(request,
                                                       report_id,
                                                       ticket.id)
        except Exception as e:
            LOG.exception(e)
            exceptions.handle(request,
                              _("Unable to create ticket."),
                              redirect=self.failure_url)


class ShowTicket(tables.LinkAction):
    name = "show_ticket"
    verbose_name = _("Show ticket")
    url = "horizon:helpdesk:tickets:details"
    classes = ("btn-edit",)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, 'tenant_id', None)
        return {"project_id": project_id}

    def allowed(self, request, report=None):
        """Allow terminate action if instance not currently being deleted."""
        return is_associated(report)

    def get_link_url(self, report=None):
        return urlresolvers.reverse(self.url, args=(report.ticket_id,))


class SecurityReportsTable(tables.DataTable):
    report_id = tables.Column("id",
                              link=("horizon:security:security_reports:"
                                    "details"),
                              verbose_name="id",)
    title = tables.Column("title", verbose_name=_("Title"))
    description = tables.Column("description", verbose_name=_("Description"))
    plugin_id = tables.Column("plugin_id", verbose_name=_("Plugin"))
    component_name = tables.Column("component_name",
                                   verbose_name=_("Component name"))
    description = tables.Column("description", verbose_name=_("Description"),
                                truncate=30)
    vulns = tables.Column("vulnerabilities_number",
                          verbose_name=_("Number of vulnerabilities"))
    security_rating = tables.Column("security_rating",
                                    verbose_name=_("Security rating"))
    last_date = tables.Column("last_report_date", verbose_name=_("Scan date"))
    project_id = tables.Column("project_id", verbose_name=_("Project"))

    class Meta:
        name = "security_reports"
        verbose_name = _("Security Reports")
        row_actions = (CreateTicket, ShowTicket)


class VulnerabilitiesTable(tables.DataTable):
    service = tables.Column("service",
                            verbose_name=_("Service"))

    family = tables.Column("family", verbose_name=_("Family"))

    name = tables.Column("name", verbose_name=_("Name"))

    risk = tables.Column("score",
                         verbose_name=_("Risk"))

    vuln_state = tables.Column('vuln_state',
                               verbose_name=_("State"))

    def get_object_id(self, vulnerability):
        return vulnerability.get('id', None)

    class Meta:
        name = "vulnerabilities"
        verbose_name = _("Vulnerabilities")
