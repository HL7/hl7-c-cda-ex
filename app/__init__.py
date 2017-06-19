#   from .views import application

import uuid
from flask import (
    Flask,
    request,
    make_response,
    session,
    redirect,
    url_for,
    jsonify,
    current_app,
    render_template,
)

import configparser
import ipdb


config = configparser.ConfigParser()
config.read('app/config.ini')

application = Flask(__name__)
application.config.update(
        SECRET_KEY=config['GENERAL']['SECRET_KEY'],
)
#   mail = Mail(application)

from app.views import application
