scrapy-sentry
=============

Logs Scrapy exceptions into Sentry

A python library that glues [Sentry](http://www.getsentry.com) with [Scrapy](http://www.scrapy.org).


Requisites: 
-----------

* [Sentry server](http://www.getsentry.com/)

Installation
------------

```bash
pip install scrapy-sentry
```

Setup
-----

To use scrapy-sentry extensions and middleware, you can set the `SENTRY_DSN` as an environment variable. Alternatively, you can set the `SENTRY_DSN` setting in your Scrapy project settings.

```python
# In your Scrapy settings
SENTRY_DSN = 'http://public:secret@example.com/1'
```

The **Errors** extension logs any Exception raised by a spider to Sentry. Enable it by adding it to the `EXTENSIONS` settings dictionary:

```python
# In your Scrapy settings
EXTENSIONS = {
    "scrapy_sentry.extensions.Errors": 10,
}
```

The **Log** extension forwards Scrapy logs to the standard Python logger. Enable it by adding it to the `EXTENSIONS` settings dictionary:

```python
EXTENSIONS = {
    "scrapy_sentry.extensions.Logs": 10,
}
```

Internally this uses the [PythonLoggingObserver](http://twistedmatrix.com/documents/current/core/howto/logging.html) feature of Twisted.

The **Signals** extension logs Scrapy signals to Sentry. Enable it by adding it to the `EXTENSIONS` settings dictionary and specifying the signals as a sequence of strings you wish to log in `SENTRY_SIGNALS`:

```python
EXTENSIONS = {
    "scrapy_sentry.extensions.Signals": 10,
}

SENTRY_SIGNALS = (
    'engine_started',
    'engine_stopped',
    # 'item_dropped',
    # 'item_passed',
    # 'item_scraped',
    # 'request_received',
    # 'response_downloaded',
    # 'response_received',
    'spider_closed',
    # 'spider_error',
    'spider_idle',
    'spider_opened',
    # 'stats_spider_closed',
    # 'stats_spider_closing',
    # 'stats_spider_opened',
)
```

Customization
-------------

**Customize the Raven Client**

To customize the arguments used to instantiate a Raven Client, scrapy-sentry offers a way to define a class or function that when called with the Sentry DSN value, will return the client instance. Define your class or function in a module, than add its absolute import path to the `SENTRY_CLIENT` key in the settings:

```python
SENTRY_CLIENT = 'utils.get_sentry_client'  # default: 'raven.Client'
```

Then in `utils.py`:

```python
from raven import Client

def get_sentry_client(dsn):
    return Client(dsn=dsn, site='my-site-name', environment='staging')
```
