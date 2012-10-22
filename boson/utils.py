# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import re
import uuid


serialize_re = re.compile(r"""[/%="']""")
deserialize_re = re.compile(r'%([0-9A-Fa-f]{2})')


def _serialize(value):
    """
    Serialize a single value.  Accepts all value types recognized by
    JSON except for floats.  Returns an encoded string.
    """

    if value is None:
        return 'null'
    elif value is True:
        return 'true'
    elif value is False:
        return 'false'
    elif isinstance(value, (int, long)):
        return str(value)
    elif isinstance(value, basestring):
        return '"%s"' % serialize_re.sub(lambda x: '%%%02X' % ord(x.group(0)),
                                         value)
    else:
        raise ValueError("Cannot encode value %r" % value)


def _deserialize(value):
    """
    Deserialize a single value.  Accepts all value types recognized by
    JSON except for floats.  Returns the decoded value.
    """

    if (value[:1], value[-1:]) in [('"', '"'), ("'", "'")]:
        return deserialize_re.sub(lambda x: chr(int(x.group(1), 16)),
                                  value[1:-1])
    elif value.isdigit():
        return int(value)
    else:
        try:
            return dict(null=None, true=True, false=False)[value.lower()]
        except KeyError:
            raise ValueError("Cannot decode value %r" % value)


def dict_serialize(data):
    """
    Serialize a data dictionary into a single string with consistent
    key ordering.  This format is suitable for table searching.
    """

    result = ['%s=%s' % (k, _serialize(v)) for k, v in
              sorted(data.items(), key=lambda x: x[0])]

    return '/'.join(result)


def dict_deserialize(data):
    """
    Deserialize a data string, as generated by dict_serialize(), into
    an appropriate data dictionary.
    """

    result = {}
    for comp in data.split('/'):
        key, value = comp.split('=')
        result[key] = _deserialize(value)

    return result


def generate_uuid():
    """
    Generate and return a string UUID.
    """

    return str(uuid.uuid4())
