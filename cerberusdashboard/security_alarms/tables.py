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


def is_associated(alarm):
    ticket_id = getattr(alarm, "ticket_id", None)
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
        'horizon:security:security_alarms:index')

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, 'tenant_id', None)
        return {"project_id": project_id}

    def allowed(self, request, alarm=None):
        """Allow terminate action if instance not currently being deleted."""
        return not(is_associated(alarm))

    def action(self, request, alarm_id):
        alarm = api.cerberus.security_alarm_get(request, alarm_id)
        if alarm.project_id is not None:
            data = {'project': alarm.project_id, 'title': alarm.summary}
        else:
            data = {'project': 'infra', 'title': alarm.summary}
        try:
            ticket = api.cerberus.ticket_create(request, data)
            api.cerberus.security_alarm_put_ticket_id(request,
                                                      alarm.alarm_id,
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

    def allowed(self, request, alarm=None):
        """Allow terminate action if instance not currently being deleted."""
        return is_associated(alarm)

    def get_link_url(self, alarm=None):
        return urlresolvers.reverse(self.url, args=(alarm.ticket_id,))


class SecurityAlarmsTable(tables.DataTable):
    alarm_id = tables.Column("alarm_id",
                             link=("horizon:security:security_alarms:"
                                   "details"),
                             verbose_name="id",)
    summary = tables.Column("summary", verbose_name=_("Summary"))
    description = tables.Column("description", verbose_name=_("Description"),
                                truncate=30)
    project_id = tables.Column("project_id", verbose_name=_("Project"))
    plugin_id = tables.Column("plugin_id", verbose_name=_("Plugin"))
    received_at = tables.Column("timestamp", verbose_name=_("Received at"))

    def get_object_id(self, datum):
        return datum.alarm_id

    class Meta:
        name = "security_alarms"
        verbose_name = _("Security Alarms")
        row_actions = (CreateTicket, ShowTicket)
