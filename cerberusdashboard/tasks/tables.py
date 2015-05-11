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


def is_recurrent(task):
    type = getattr(task, "type", None)
    if not type:
        return False
    return type.lower() == "recurrent"


def is_stopped(task):
    state = getattr(task, "state", None)
    if not state:
        return False
    return state.lower() == "stopped"


class DeleteTasks(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("%(data_type)s deleted")
    data_type_singular = _("Task")
    data_type_plural = _("Tasks")
    classes = ('btn-danger')
    failure_url = urlresolvers.reverse_lazy(
        'horizon:security:tasks:index')

    def allowed(self, request, task=None):
        """Allow terminate action if instance not currently being deleted."""
        return is_recurrent(task)

    def action(self, request, obj_id):
        try:
            api.cerberus.task_delete(request, obj_id)
        except Exception as e:
            LOG.exception(e)
            exceptions.handle(request,
                              _("Unable to delete ticket."),
                              redirect=self.failure_url)


class RestartTasks(tables.BatchAction):
    name = "restart"
    action_present = _("Restart")
    action_past = _("%(data_type)s restarted")
    data_type_singular = _("Task")
    data_type_plural = _("Tasks")
    classes = ('btn-danger')
    failure_url = urlresolvers.reverse_lazy(
        'horizon:security:tasks:index')

    def allowed(self, request, task=None):
        """Allow terminate action if instance not currently being deleted."""
        return is_recurrent(task) and is_stopped(task)

    def action(self, request, obj_id):
        try:
            api.cerberus.task_restart(request, obj_id)
        except Exception as e:
            LOG.exception(e)
            exceptions.handle(request,
                              _("Unable to restart ticket."),
                              redirect=self.failure_url)


class StopTasks(tables.BatchAction):
    name = "stop"
    action_present = _("Stop")
    action_past = _("%(data_type)s stopped")
    data_type_singular = _("Task")
    data_type_plural = _("Tasks")
    classes = ('btn-danger', 'btn-terminate')
    failure_url = urlresolvers.reverse_lazy(
        'horizon:security:tasks:index')

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, 'tenant_id', None)
        return {"project_id": project_id}

    def action(self, request, obj_id):
        try:
            api.cerberus.task_stop(request, obj_id)
        except Exception as e:
            LOG.exception(e)
            exceptions.handle(request,
                              _("Unable to stop task."),
                              redirect=self.failure_url)


class TasksTable(tables.DataTable):
    id = tables.Column("id",
                       link=("horizon:security:tasks:details"),
                       verbose_name="id",)
    name = tables.Column("name", verbose_name=_("Name"))
    type = tables.Column("type", verbose_name=_("Type"))
    period = tables.Column("period", verbose_name=_("Period"))
    state = tables.Column("state", verbose_name=_("State"))
    plugin_id = tables.Column("plugin_id", verbose_name=_("Plugin"))

    class Meta:
        name = "tasks"
        verbose_name = _("Tasks")
        table_actions = (DeleteTasks, StopTasks, RestartTasks)
        row_actions = (DeleteTasks, StopTasks, RestartTasks)
