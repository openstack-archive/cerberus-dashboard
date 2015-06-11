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

from cerberusclient import client as cerberus_client
from horizon.utils.memoized import memoized  # noqa
from openstack_dashboard.api import base
try:
    from sticksclient import client as sticks_client
    from sticksclient.common import exceptions as sticks_exc
except ImportError:
    sticks_exc = None
    sticks_client = None
    pass

from cerberusdashboard.utils import importutils

keystone = importutils.import_any('openstack_dashboard.api.keystone',
                                  'horizon.api.keystone')

LOG = logging.getLogger(__name__)


@memoized
def cerberusclient(request):
    """Initialization of Cerberus client."""
    cerberus_endpoint = base.url_for(request, 'security')
    return cerberus_client.Client('1',
                                  cerberus_endpoint,
                                  tenant_id=request.user.tenant_id,
                                  token=request.user.token.id)


@memoized
def sticksclient(request):
    """Initialization of Cerberus client."""
    sticks_endpoint = base.url_for(request, 'helpdesk')
    return sticks_client.Client('1',
                                sticks_endpoint,
                                tenant_id=request.user.tenant_id,
                                token=request.user.token.id)


def plugin_list(request):
    """List plugins."""
    return cerberusclient(request).plugins.list()


def plugin_get(request, plugin_id):
    """Get plugin information."""
    return cerberusclient(request).plugins.get(plugin_id)


def task_list(request):
    """List tasks."""
    return cerberusclient(request).tasks.list()


def task_get(request, task_id):
    """Get specific task."""
    return cerberusclient(request).tasks.get(task_id)


def task_create(request, plugin_id, method, name='unknown', type='unique',
                period=None):
    """Create a task."""
    return cerberusclient(request).tasks.create(
        plugin_id, method, name, type, period)


def task_stop(request, task_id):
    """Stop specific task."""
    return cerberusclient(request).tasks.stop(task_id)


def task_restart(request, task_id):
    """Stop specific task."""
    return cerberusclient(request).tasks.restart(task_id)


def task_delete(request, task_id):
    """Delete specific task."""
    return cerberusclient(request).tasks.delete(task_id)


def task_force_delete(request, task_id):
    """Force delete specific task."""
    return cerberusclient(request).tasks.force_delete(task_id)


def security_report_list(request):
    """List the security reports."""
    return cerberusclient(request).security_reports.list()


def security_report_get(request, sr_uuid):
    """Get a security report."""
    return cerberusclient(request).security_reports.get(sr_uuid)


def security_report_put_ticket_id(request, sr_uuid, ticket_id):
    """Update a security report by adding its associated ticket id."""
    return cerberusclient(request).security_reports.put(sr_uuid, ticket_id)


def security_alarm_list(request):
    """List the security alarms."""
    return cerberusclient(request).security_alarms.list()


def security_alarm_get(request, security_alarm_id):
    """Get a security alarm."""

    return cerberusclient(request).security_alarms.get(security_alarm_id)


def security_alarm_put_ticket_id(request, sa_id, ticket_id):
    """Update a security report by adding its associated ticket id."""
    return cerberusclient(request).security_alarms.put(sa_id, ticket_id)


def ticket_create(request, data):
    """Create a ticket from a security report."""
    return sticksclient(request).tickets.create(data)


def is_sticks_available(request):
    """Create a ticket from a security report."""
    if sticks_client is None:
        LOG.exception("No module named sticksclient")
        return False
    try:
        return isinstance(sticksclient(request).tickets.list(
            data={'project': request.user.tenant_id}), list)
    except sticks_exc.CommunicationError as e:
        LOG.exception(e)
        return False
