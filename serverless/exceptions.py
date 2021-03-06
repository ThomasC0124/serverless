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

"""
Serverless Exceptions


.. _Supported status codes when using lambda-proxy:
   https://serverless.com/framework/docs/providers/aws/events/apigateway#status-codes

"""


class ServerlessError(Exception):
    """Base class for exceptions raised raised by serverless app

    Args:
        message: the exception message
        errors: an optional list of error details
    """
    status_code = 500

    def __init__(self, message='', errors=()):
        super(ServerlessError, self).__init__(message)
        self.message = message
        self.errors = errors


class ClientError(ServerlessError):
    """Base class for all client error (HTTP 4xx) responses"""


class BadRequest(ClientError):
    """Exception mapping a ``400 Bad Request`` response."""
    status_code = 400


class Unauthorized(ClientError):
    """Exception mapping a ``401 Unauthorized`` response."""
    status_code = 401


class Forbidden(ClientError):
    """Exception mapping a ``403 Forbidden`` response."""
    status_code = 403


class NotFound(ClientError):
    """Exception mapping a ``404 Not Found`` response."""
    status_code = 404


class UnprocessableEntity(ClientError):
    """Exception mapping a ``422 Unprocessable Entity`` response."""
    status_code = 422
