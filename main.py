#!/usr/bin/env python

"""Application instance and handlers instantiation."""
from collections import defaultdict
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application as TornadoApp
from tornado.options import options, define, parse_config_file

import settings

# Options
define("port", type=int)
define("app_debug", type=bool)


def extend_handlers(name):
    """Load the (URL pattern, handler) tuples for each component."""
    mod = __import__(name, fromlist=['handlers'])
    return mod.handlers


class Application(TornadoApp):
    """Tornado Application instance"""
    def __init__(self):
        """Handlers and other settings initialization"""
        handlers = []
        handlers.extend(extend_handlers('handlers.auth'))
        handlers.extend(extend_handlers('handlers.bank'))
        # Static handlers should always go last.
        # /(*) in static handler matches every URL.
        handlers.extend(extend_handlers('handlers.static'))
        _settings = dict(
            cookie_secret="njasduuqwheazmu293nsadhaslzkci9023nsadnua9sdadsVo",
            debug=options.app_debug, compress_response=True)
        TornadoApp.__init__(self, handlers, **_settings)
        self.geo_jsons_cache = defaultdict(dict)


def main():
    """Initialise application and run instance."""
    parse_config_file(settings.APP_CONF)
    http_server = HTTPServer(Application())
    http_server.listen(options.port)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
