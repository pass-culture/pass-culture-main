# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

cfg = None
_NOT_FOUND = object()


def get_oslo_config():
    """Runtime load the oslo.config object.

    In performance optimization of openstackclient it was determined that even
    optimistically loading oslo.config if available had a performance cost.
    Given that we used to only raise the ImportError when the function was
    called also attempt to do the import to do everything at runtime.
    """
    global cfg

    # First Call
    if not cfg:
        try:
            from oslo_config import cfg
        except ImportError:
            cfg = _NOT_FOUND

    if cfg is _NOT_FOUND:
        raise ImportError("oslo.config is not an automatic dependency of "
                          "keystoneauth. If you wish to use oslo.config "
                          "you need to import it into your application's "
                          "requirements file. ")

    return cfg
