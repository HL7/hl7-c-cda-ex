from app import application
from app.sync2 import sync

import os

ROOTDIR = os.path.abspath(os.path.dirname(__file__))

application.jinja_loader.searchpath=[os.path.normpath(os.path.join(ROOTDIR,'templates'))]
application.static_folder=os.path.normpath(os.path.join(ROOTDIR,'static'))
import os
if 'APP_URI' in os.environ and 'APP_PORT' in os.environ:
    host = os.environ['APP_URI']
    port = int(os.environ['APP_PORT'])
else:
    host = '127.0.0.1'
    port = 7000

if __name__ == "__main__":


    application.run(host=host, port=port, debug=True)
