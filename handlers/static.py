"""Static component handlers of the application."""

from os.path import join
from tornado.web import StaticFileHandler, url

import settings
from tornado.web import RequestHandler

BOWER_DIR = join(settings.CURR_DIR, 'bower_components')
DOCS_DIR = join(settings.CURR_DIR, 'docs')
STATIC_DIR = join(settings.CURR_DIR, 'app')
INDEX_HTML = join(STATIC_DIR, 'index.html')
LOGIN_HTML = join(STATIC_DIR, 'login.html')


class IndexHTMLHandler(RequestHandler):
    """Landing page - Index page request handler."""
    def get(self):
        self.render(INDEX_HTML)


class LoginHTMLHandler(RequestHandler):
    """Login page - Login page request handler."""
    def get(self):
        self.render(LOGIN_HTML)


handlers = [
    url(r'/', IndexHTMLHandler),
    url(r'/bower_components/(.*)', StaticFileHandler, {'path': BOWER_DIR}),
    url(r'/docs/(.*)', StaticFileHandler, {'path': DOCS_DIR}),
    url(r'/login', LoginHTMLHandler),
    url(r'/(.*)', StaticFileHandler, {'path': STATIC_DIR})
]
