import os
import time
import logging

from twisted.python import log

from scrapy.conf import settings
from scrapy.exceptions import NotConfigured
from scrapy.http import Request, Headers
from scrapy.utils.reqser import request_to_dict, request_from_dict
from scrapy.responsetypes import responsetypes

from raven.base import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from pydoc import locate


def init(dsn=None):
    """Redirect Scrapy log messages to standard Python logger"""

    observer = log.PythonLoggingObserver()
    observer.start()

    dict_config = settings.get("LOGGING")
    if dict_config is not None:
        assert isinstance(dict_config, dict)
        logging.dictConfig(dict_config)

    handler = SentryHandler(dsn)
    setup_logging(handler)


def response_to_dict(response, spider, include_request=True, **kwargs):
    """Returns a dict based on a response from a spider"""
    d = {
        'time': time.time(),
        'status': response.status,
        'url': response.url,
        'headers': dict(response.headers),
        'body': response.body,
      }
    if include_request:
        d['request'] = request_to_dict(response.request, spider)
    return d


def response_from_dict(response, spider=None, **kwargs):
    """Returns a dict based on a response from a spider"""
    url = response.get("url")
    status = response.get("status")
    headers = Headers([(x, map(str, y)) for x, y in
                       response.get("headers").iteritems()])
    body = response.get("body")

    respcls = responsetypes.from_args(headers=headers, url=url)
    response = respcls(url=url, headers=headers, status=status, body=body)
    return response


class TempStoreClient(Client):
    def __init__(self, **kwargs):
        self.events = []
        super(TempStoreClient, self).__init__(**kwargs)

    def is_enabled(self):
        return True

    def send(self, **kwargs):
        self.events.append(kwargs)


class RavenClient(object):

    @classmethod
    def from_crawler(cls, crawler):
        if hasattr(crawler, 'raven_client'):
            return crawler.raven_client
        raven_class = crawler.settings.get('RAVEN_CLASS', 'raven.Client')
        dsn = crawler.settings.get('RAVEN_DSN', None)
        if not dsn:
            raise NotConfigured('No RAVEN_DSN is configured')
        klass = locate(raven_class)
        crawler.raven_client = klass(dsn=dsn)
        return crawler.raven_client

