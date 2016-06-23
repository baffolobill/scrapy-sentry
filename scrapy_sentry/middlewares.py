import sys

from scrapy import log

from .utils import RavenClient


class SentryMiddleware(RavenClient):

    @classmethod
    def from_crawler(cls, crawler):
        cls.raven_client = super().from_crawler(crawler)
        return cls()

    def trigger(self, exception, spider=None, extra={}):
        extra = {
                'spider': spider.name if spider else "",
            }
        msg = self.raven_client.captureException(exc_info=sys.exc_info(), extra=extra)
        ident = self.raven_client.get_ident(msg)

        l = spider.log if spider else log.msg
        l("Sentry Exception ID '%s'" % ident, level=log.INFO)

        return None
        
    def process_exception(self, request, exception, spider):
        return self.trigger(exception, spider, 
                            extra={"spider":spider, "request":request})

    def process_spider_exception(self, response, exception, spider):
        return self.trigger(exception, spider, 
                            extra={"spider":spider, "response":response})

