"""
Send signals to Sentry

Use SENTRY_DSN setting to enable sending information
"""
import logging
import os

from scrapy import signals
from scrapy.mail import MailSender
from scrapy.exceptions import NotConfigured

from .utils import RavenClient, response_to_dict


class Log(RavenClient):

    @classmethod
    def from_crawler(cls, crawler):
        super().from_crawler(crawler)
        return cls()


class Signals(RavenClient):

    @classmethod
    def from_crawler(cls, crawler):
        cls.raven_client = super().from_crawler(crawler)
        o = cls()
        sentry_signals = crawler.settings.get("SENTRY_SIGNALS", [])
        if len(sentry_signals):
            receiver = o.signal_receiver
            for signalname in sentry_signals:
                signal = getattr(signals, signalname)
                crawler.signals.connect(receiver, signal=signal)
        return o
        
    def signal_receiver(self, signal=None, sender=None, *args, **kwargs):
        message = signal
        extra = {
                'sender': sender,
                'signal': signal,
                'args': args,
                'kwargs': kwargs,
            }
        idents = []
        msg = self.raven_client.capture('Message', message=message, extra=extra)
        ident = self.raven_client.get_ident(msg)
        return ident


class Errors(RavenClient):

    @classmethod
    def from_crawler(cls, crawler):
        cls.raven_client = super().from_crawler(crawler)
        o = cls()
        crawler.signals.connect(o.spider_error, signal=signals.spider_error)
        return o 

    def spider_error(self, failure, response, spider, signal=None, sender=None, *args, **kwargs):
        from six import StringIO
        traceback = StringIO()
        failure.printTraceback(file=traceback)

        message = signal
        extra = {
                'sender': sender,
                'spider': spider.name,
                'signal': signal,
                'failure': failure,
                'response': response_to_dict(response, spider, include_request=True),
                'traceback': "\n".join(traceback.getvalue().split("\n")[-5:]),
            }
        msg = self.raven_client.captureMessage(
            message=u"[{}] {}".format(spider.name, repr(failure.value)),
            extra=extra) #, stack=failure.stack)
            
        ident = self.raven_client.get_ident(msg)

        l = spider.log if spider else ""
        l("Sentry Exception ID '%s'" % ident, level=logging.INFO)

        return ident

