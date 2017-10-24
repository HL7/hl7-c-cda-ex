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
    g
)
from app import application

import configparser
import ipdb
from pygments import highlight
from pygments.lexers import XmlLexer, guess_lexer
from pygments.formatters import HtmlFormatter
from bson.objectid import ObjectId

from .sync import sync

config = configparser.ConfigParser()
config.read('app/config.ini')

application = Flask(__name__)
application.config.update(
        SECRET_KEY=config['GENERAL']['SECRET_KEY']
)

from db import db
from bson.objectid import ObjectId

#application.register_blueprint(search)
#search.config=config

@application.route('/', methods=['GET', 'POST'])
@application.route('/sections', methods=['GET', 'POST'])
def get_list_sections_page():
    examples = db.sections.find({}).sort("name", 1)
    #   return render_template("orig.html", examples=examples)
    return render_template("sections.html", examples=examples)


@application.route('/sections/<section_id>', methods=['GET', 'POST'])
def get_section_page(section_id):
    section = db.sections.find_one({"_id": ObjectId(section_id)})
    examples = db.examples.find({"section": section['name']}).sort("name", 1)
    #   return render_template("orig.html", examples=examples)
    return render_template("examples.html", section=section, examples=examples)

@application.route('/examples/view/<permalink_id>', methods=['GET', 'POST'])
def get_example_page(permalink_id):
    #   example = db.examples.find_one({"Permalink": ObjectId(permalink_id)})
    #   example = db.examples.find_one({"Permalink": permalink_id})
    obj_id = False
    try:
        obj_id = ObjectId(permalink_id)
    except Exception as e:
        obj_id = False
    if obj_id:
        example = db.examples.find_one({"Permalink": {
                "$in": [permalink_id, obj_id],
            }
        })
    else:
        example = db.examples.find_one({"Permalink": permalink_id})

    if not example:
        pass #  TODO: handle if this doesn't work
    if example['xml']:
        #   TODO: let's just set the lexer intead of guessing its
        lexer = XmlLexer() #  guess_lexer(example['xml'])
        style = HtmlFormatter(style='friendly').style
        #   ipdb.set_trace()
        xml = highlight(example['xml'], lexer, HtmlFormatter(full=True, style='colorful'))
    else:
        xml = None
    #   return render_template("orig.html", examples=examples)
    return render_template("example.html", example=example, xml=xml)

@application.route("/examples/download/<permalink_id>", methods=['GET', 'POST'])
def download_example(permalink_id):
    example = db.examples.find_one({"Permalink": permalink_id})
    response = make_response(example['xml'])
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename={}.xml".format(example['name'])
    return response

@application.route('/search', methods=['GET', 'POST'])
def get_search_results():
    if request.method == 'GET':
        return get_list_sections_page()

    query = {}
    #   ipdb.set_trace()
    params = dict(request.form)
    import re
    terms = '.*{}.*'.format(str(params['search_terms'][0]))

    regx = re.compile(terms, re.IGNORECASE)
    #   ipdb.set_trace()

    if 'search_terms' in params and params['search_terms'] != '':
        #query['name'] = {"$regex": '/*.{}*./i'.format(str(params['search_terms'][0]))}
        query['name'] = {"$regex": regx}

    if 'approval' in params:
        query['approval'] = {"$in": params['approval']}

    if 'certification' in params and params['certification'][0] == '1':
        query['Certification'] = 'ONC'

    #   ipdb.set_trace()

    examples = db.examples.find(query)
    print params
    print query
    return render_template("search_results.html", examples=examples)


@application.route('/sync', methods=['GET', 'POST'])
@application.route('/sync/<permalink_id>', methods=['GET', 'POST'])
def sync_from_github(permalink_id=None):
    if(permalink_id):
        return jsonify(sync(permalink_id))
    else:
        return jsonify(sync())

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
