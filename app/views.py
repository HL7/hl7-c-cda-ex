import uuid, urllib, urllib2, base64, os
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
    g
)
from app import application

import configparser
import ipdb
import requests

from .sync2 import sync
from repo import get_sections, get_section, get_example, get_file, search, generate_permalink

config = configparser.ConfigParser()
config.read('app/config.ini')

application = Flask(__name__)
application.config.update(
        SECRET_KEY=config['GENERAL']['SECRET_KEY']
)

from db import db, GIT_URL, GIT_BRANCH
from bson.objectid import ObjectId

#application.register_blueprint(search)
#search.config=config

@application.route('/', methods=['GET', 'POST'])
@application.route('/sections', methods=['GET', 'POST'])
def get_list_sections_page():
    sections = get_sections()
    return render_template("sections.html", sections=sections)


@application.route('/sections/<name>', methods=['GET', 'POST'])
def get_section_page(name):
    section, examples = get_section(name)

    return render_template("examples.html", section=section, examples=examples)


@application.route('/examples/view/<section_slug>/<example_slug>', methods=['GET', 'POST'])
@application.route('/examples/view/<section_slug>/<section_sha>/<example_slug>/<example_sha>', methods=['GET', 'POST'])
def get_example_page(section_slug,example_slug,section_sha=None, example_sha=None):

    section, readme, example_files = get_example(section_slug, example_slug)
    return render_template("readme_example.html",
                            section=section,
                            readme=readme,
                            example_files=example_files)


@application.route('/examples/view/<permalink_id>', methods=['GET', 'POST'])
def get_example_page_by_permalink_id(permalink_id):
    example = db.examples.find_one({"PermalinkId": permalink_id})
    if not example:
        return 'error'

    section, readme, example_files = get_example(example['section'], example['name'])

    return render_template("readme_example.html",
                            section=section,
                            readme=readme,
                            example_files=example_files)


@application.route("/examples/download/<section>/<example>/<filename>", methods=['GET', 'POST'])
def download_example(section,example,filename):
    content = get_file(section,example,filename)
    response = make_response(content)
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
    return response

@application.route('/search', methods=['GET', 'POST'])
def get_search_results():
    if request.method == 'GET':
        return get_list_sections_page()

    query = {}
    #   ipdb.set_trace()
    params = dict(request.form)
    import re
    #terms = '.*{}.*'.format(str(params['search_terms'][0]))
    terms = '{}'.format(str(params['search_terms'][0]))

    criteria = []
    if terms != '""':
        criteria.append(terms)
    STATUSES = ['Approved', 'Withdrawn', 'Pending']
    status = params['approval'][0] if 'approval' in params else None
    #if 'approval' in params:
    #    #   terms = '{} AND "Approval Status: {}"'.format(terms, params['approval'][0])
    #    approval_query = '"Approval Status: {}"'.format(params['approval'][0])
    #    criteria.append(approval_query)

    onc_certified = True if 'certification' in params and params['certification'][0] == '1' else None
    #    #   terms = '{} AND "Certification ONC"'.format(terms)
    #    onc_cert_query = '"Certification ONC"'
    #    criteria.append(onc_cert_query)

    examples = search(terms, status, onc_certified )

    #   query = " AND ".join(criteria)

    return render_template("search_results.html", results=examples)



@application.route('/do-sync', methods=['GET', 'POST'])
def sync_from_github():
    status, repo = sync(operation='sync')
    git = {'url': GIT_URL, 'branch': GIT_BRANCH}
    msg = repo if not status else ''
    return render_template("request_sync.html", git=git, status=status, msg=msg)



@application.route('/sync', methods=['GET', 'POST'])
def request_sync():
    git = {'url': GIT_URL, 'branch': GIT_BRANCH}
    return render_template("request_sync.html", git=git)

@application.route('/permalink/generate/<section>/<example>/<readme>', methods=['GET', 'POST'])
def request_new_permalink(section, example, readme):
    completed, msg = generate_permalink(section, example, readme)
    return render_template("request_permalink.html", section=section, example=example, msg=msg)



import configparser

@application.before_request
def before_request():
    print "initialize db"

"""
@application.errorhandler(404)
def not_found(error):
    isAPI=False
    try:
        isAPI=request.path.lower().startswith('/api/')
    except:pass
    if isAPI:
        return make_response(jsonify({'error':'Not found' if error.code==404 else error.description}),error.code)
    return render_template('error.html',error=error),error.code
"""

@application.route("/down")
def down():
    return render_template("down.html")
