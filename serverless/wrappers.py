# -*- coding: utf-8 -*-
#
# Copyright 2020 Evolent Health, Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Serverless wrapper classes"""
from datetime import date, datetime
import json
import logging
import uuid

from serverless.compat import JSONDecodeError
from serverless.exceptions import BadRequest


class ServerlessJsonEncoder(json.JSONEncoder):
    """
    The default Serverless JSON encoder. This one extends python's default json encoder to
    support serialization of ``date``, ``datetime`` and ``UUID`` objects.

    NOTE: ISO-8601 format willbe used for date serialization.
    """
    def default(self, o): # pylint: disable=E0202
        """Serializes object"""
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if isinstance(o, uuid.UUID):
            return str(o)
        return json.JSONEncoder.default(self, o)


class Request:
    """
    Request wrapper class to help precessing AWS Lambda input

    Args:
        event (dict): AWS Lambda event
        context (LambdaContext): AWS Lambda context

    Attributes:
        event (dict): AWS Lambda event
        context (LambdaContext): AWS Lambda context
        data (dict): request body
        query (dict): query string parameters
        params (dict): path parameters

    Raises:
        BadRequest: if event['body'] is not None and not deserializable

    .. _AWS Lambda python programming model:
       http://docs.aws.amazon.com/lambda/latest/dg/python-programming-model-handler-types.html
    """
    def __init__(self, event, context):
        self.event = event
        self.context = context
        self._data = None
        self.logger = logging.getLogger(__name__)

    @property
    def data(self):
        """
        Parses event and return body as dict

        Returns:
            data (dict): a dict containing event['body'] data

        Raises:
            AttributeError: if event is not dict like object
            JSONDecodeError: if event body is not a valid JSON document

        .. _JSONDecodeError:
           https://docs.python.org/3/library/json.html#json.JSONDecodeError
        """
        if not self._data:
            body = self.event.get('body', None)
            if not isinstance(body, dict):
                try:
                    self._data = json.loads(body) if body else dict()
                except JSONDecodeError as e:
                    self.logger.info('Failed to decode request body=%r', body)
                    errors = (str(e))
                    raise BadRequest('Malformed request body', errors)
            else:
                self._data = body
        return self._data

    @property
    def query(self):
        """
        Returns HTTP query string as dict

        Raises:
            AttributeError: if event is not dict like object
        """
        return self.event.get('queryStringParameters', dict())

    @property
    def params(self):
        """
        Returns HTTP path params as dict

        Raises:
            AttributeError: if event is not dict like object
        """
        return self.event.get('pathParameters', dict())


class Response:
    """
    Response wrapper class to help formmating output compatible with AWS Lambda

    Args:
        data (dict): data to populate response body
        status_code (int): response status code
        headers (dict): response headers
    """
    _security_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'Cache-Control': 'no-cache, must-revalidate',
        'Pragma': 'no-cache',
        'X-XSS-Protection': '1; mode=block'
    }

    def __init__(self, data=None, status_code=200, headers=None):
        self.data = data
        self.status_code = status_code
        self.headers = self._security_headers.copy()

        if headers:
            self.headers.update(headers)

    @property
    def body(self):
        """Returns string representation of body"""
        return json.dumps(self.data, cls=ServerlessJsonEncoder)

    def to_lambda_output(self):
        """
        Returns AWS Lambda compatible response populated with
        the given data, status_code, and headers.
        By default, it uses ServerlessJsonEncoder for serialization.

        Returns:
            resp (dict): AWS Lambda compatible response data

        Raises:
            TypeError: if self.data is not JSON serializable
        """
        resp = {
            'statusCode': self.status_code,
            'body': self.body,
            'headers': self.headers
        }

        return resp
