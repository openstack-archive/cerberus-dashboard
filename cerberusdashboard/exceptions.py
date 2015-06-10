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

from cerberusclient.common import exceptions as cerberusclient
try:
    from sticksclient.common import exceptions as sticksclient
    # HTTPInternalServerError is thrown by Redmine when project does not exist
    # This error may change in the future (refer to sticks client)
    RECOVERABLE = (sticksclient.HTTPInternalServerError,)
except ImportError:
    RECOVERABLE = ()
    pass

NOT_FOUND = (cerberusclient.HTTPNotFound,)
