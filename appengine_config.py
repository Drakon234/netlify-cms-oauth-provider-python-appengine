from gaesessions import SessionMiddleware
from google.appengine.ext import vendor
import datetime
import os

# Add any libraries installed in the "lib" folder.
vendor.add('lib')


def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(
        app,
        cookie_key=os.urandom(64),
        cookie_only_threshold=0,
        lifetime=datetime.timedelta(minutes=5),
        no_datastore=True)
    return app
