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
from pygments import highlight
from pygments.lexers import XmlLexer, guess_lexer
from pygments.formatters import HtmlFormatter
from bson.objectid import ObjectId
import markdown2
import requests
from md2py import md2py

from .sync import sync

config = configparser.ConfigParser()
config.read('app/config.ini')
GITHUB_PERSONAL_TOKEN = os.environ['GITHUB_PERSONAL_TOKEN']

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
    url = "https://api.github.com/repos/HL7/C-CDA-Examples/git/trees/4ab475857608c821b057d926fb9edda44793c635"
    #   url = 'https://api.github.com/search/code?q="Section Examples from C-CDA"++repo:HL7/C-CDA-Examples+extension:md'
    response = requests.get(url, headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
    sections = []
    for item in response.json()['tree']:
        # only include directories for each section
        if item['type'] == 'tree':
             sections.append({
                "name": item['path'],
                "slug": urllib.quote(item['path']),
                "sha": item['sha']
             })
    return render_template("sections.html", sections=sections)


@application.route('/sections/<slug>/<sha>', methods=['GET', 'POST'])
def get_section_page(slug, sha):
    url = "https://api.github.com/repos/HL7/C-CDA-Examples/git/trees/{}".format(sha)
    response = requests.get(url, headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
    section = {"name": urllib.unquote(slug), "slug":slug, "sha": sha}
    examples = []
    for item in response.json()['tree']:
        # only include directories for each example
        if item['type'] == 'tree':
            example = {
                "name": item['path'],
                "slug": urllib.quote(item['path']),
                "sha": item['sha']
            }
            section = {"name": slug, "slug":urllib.quote(slug), "sha": sha}
            data_url = 'https://api.github.com/search/code?q=repo:HL7/C-CDA-Examples+path:"/{}/{}"'.format(section['slug'], example['slug'])
            response = requests.get(data_url, headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
            for ex in response.json()['items']:
                readme = get_readme(ex['git_url'])
                #   ipdb.set_trace()
                if readme.find('Approval Status: Withdrawn') != -1:
                    example['approval_status'] = 'Withdrawn'
                if readme.find('Approval Status: Approved') != -1:
                    example['approval_status'] = 'Pending'
                if readme.find('Approval Status: Pending') != -1:
                    example['approval_status'] = 'Pending'

            examples.append(example)

    return render_template("examples.html", section=section, examples=examples)

def get_readme(git_url):
    r = requests.get(git_url, headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
    json_data = r.json()
    decoded_content = base64.b64decode(json_data['content'])
    readme = markdown2.markdown(decoded_content)
    return readme

@application.route('/sections/name/<name>', methods=['GET', 'POST'])
def get_section_by_name_page(name):
    section = db.sections.find_one({"name": urllib2.unquote(name).decode('utf8')})
    examples = db.examples.find({"section": section['name']}).sort("name", 1)
    #   return render_template("orig.html", examples=examples)
    return render_template("examples.html", section=section, examples=examples)


@application.route('/examples/view/<section_slug>/<example_slug>', methods=['GET', 'POST'])
@application.route('/examples/view/<section_slug>/<section_sha>/<example_slug>/<example_sha>', methods=['GET', 'POST'])
def get_example_page(section_slug,example_slug,section_sha=None, example_sha=None):
    section = {"name": section_slug, "slug":urllib.quote(section_slug), "sha": section_sha}
    example = {"name": example_slug, "slug":urllib.quote(example_slug), "sha": example_sha}
    data_url = 'https://api.github.com/search/code?q=repo:HL7/C-CDA-Examples+path:"/{}/{}"'.format(section['slug'], example['slug'])
    response = requests.get(data_url, headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
    readme = {}
    example_files = []
    print response.json()
    print data_url
    for item in response.json()['items']:
        print item
        # only include directories for each example
        if item['name'].lower() == 'readme.md' :
            r = requests.get(item['git_url'], headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
            json_data = r.json()
            decoded_content = base64.b64decode(json_data['content'])
            readme['content'] = markdown2.markdown(decoded_content)
            print readme
        elif item['name'].endswith('.xml'):
            r = requests.get(item['git_url'], headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
            json_data = r.json()
            decoded_content = base64.b64decode(json_data['content'])
            lexer = XmlLexer() #  guess_lexer(example['xml'])
            style = HtmlFormatter(style='friendly').style
            example_files.append({
                "name": item['name'],
                "github_link": item['html_url'],
                "content": highlight(decoded_content, lexer, HtmlFormatter(full=True, style='colorful')),
                "sha": json_data['sha']
            })

        elif item['name'].endswith('.html'):
            r = requests.get(item['git_url'], headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
            json_data = r.json()
            decoded_content = base64.b64decode(json_data['content'])
            utf8_content = decoded_content.decode("utf8")
            #lexer = XmlLexer() #  guess_lexer(example['xml'])
            #style = HtmlFormatter(style='friendly').style
            example_files.append({
                "name": item['name'],
                "github_link": item['html_url'],
                "content": utf8_content,
                "sha": json_data['sha']
            })
    print example_files
    return render_template("readme_example.html", data_url=data_url, example=example, readme=readme, example_files=example_files)


@application.route('/examples/view/<permalink_id>', methods=['GET', 'POST'])
def get_example_page_by_permalink_id(permalink_id):
    data_url = 'https://api.github.com/search/code?q="http://cdasearch.hl7.org/examples/view/{}"+repo:HL7/C-CDA-Examples+extension:md+in:file'.format(permalink_id)
    response = requests.get(data_url, headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
    readme = {}
    example_files = []
    example = {"name": 'test'}
    print response.json()
    path = response.json()['items'][0]['path']
    slugs = path.split('/')
    section = {"name": slugs[0], "slug":urllib.quote(slugs[0])}
    example = {"name": slugs[1], "slug":urllib.quote(slugs[1])}


    data_url = 'https://api.github.com/search/code?q=repo:HL7/C-CDA-Examples+path:"/{}/{}"'.format(section['slug'], example['slug'])
    response = requests.get(data_url, headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})

    for item in response.json()['items']:
        # only include directories for each example
        if item['name'].lower() == 'readme.md' :
            r = requests.get(item['git_url'], headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
            json_data = r.json()
            decoded_content = base64.b64decode(json_data['content'])
            readme['content'] = markdown2.markdown(decoded_content)
        elif item['name'].endswith('.xml'):
            r = requests.get(item['git_url'], headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
            json_data = r.json()
            decoded_content = base64.b64decode(json_data['content'])
            lexer = XmlLexer() #  guess_lexer(example['xml'])
            style = HtmlFormatter(style='friendly').style
            example_files.append({
                "name": item['name'],
                "github_link": item['html_url'],
                #   "download_url": item['download_url'],
                "content": highlight(decoded_content, lexer, HtmlFormatter(full=True, style='colorful')),
                "sha": json_data['sha']

            })
        elif item['name'].endswith('.html'):
            r = requests.get(item['git_url'], headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
            json_data = r.json()
            decoded_content = base64.b64decode(json_data['content'])
            #lexer = XmlLexer() #  guess_lexer(example['xml'])
            #style = HtmlFormatter(style='friendly').style
            example_files.append({
                "name": item['name'],
                "github_link": item['html_url'],
                #   "download_url": item['download_url'],
                "content": decoded_content,
                "sha": json_data['sha']
            })


    return render_template("readme_example.html", section=section, example=example, readme=readme, example_files=example_files)


@application.route("/examples/download/<name>/<sha>", methods=['GET', 'POST'])
def download_example(name,sha):
    data_url = 'https://api.github.com/repos/HL7/C-CDA-Examples/git/blobs/{}'.format(sha)
    r = requests.get(data_url, headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})
    blob = r.json()
    decoded_content = base64.b64decode(blob['content'])
    response = make_response(decoded_content)
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename={}".format(name)
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
    terms = '"{}"'.format(str(params['search_terms'][0]))
    criteria = []
    if terms != '""':
        criteria.append(terms)
    STATUSES = ['Approved', 'Withdrawn', 'Pending']
    if 'approval' in params:
        #   terms = '{} AND "Approval Status: {}"'.format(terms, params['approval'][0])
        approval_query = '"Approval Status: {}"'.format(params['approval'][0])
        criteria.append(approval_query)

    if 'certification' in params and params['certification'][0] == '1':
        #   terms = '{} AND "Certification ONC"'.format(terms)
        onc_cert_query = '"Certification ONC"'
        criteria.append(onc_cert_query)

    query = " AND ".join(criteria)
    data_url = 'https://api.github.com/search/code?q={}+repo:HL7/C-CDA-Examples+extension:md'.format(query)
    print data_url
    response = requests.get(data_url, headers={"Authorization": "Bearer {}".format(GITHUB_PERSONAL_TOKEN)})

    results = response.json()
    examples = []
    for item in results["items"]:
        path = item['path']
        slugs = path.split('/')
        section = {"name": slugs[0], "slug":urllib.quote(slugs[0])}
        example = {"name": slugs[1], "slug":urllib.quote(slugs[1])}
        examples.append({"section": section, "example": example})

    return render_template("search_results.html", data_url=data_url, results=examples)

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


@application.route('/do-sync', methods=['GET', 'POST'])
@application.route('/do-sync/<permalink_id>', methods=['GET', 'POST'])
def sync_from_github(permalink_id=None):
    if(permalink_id):
        status, msg = sync(operation='sync', permalink_id=permalink_id)
    else:
        status, msg = sync(operation='sync')

    return render_template("request_sync.html", permalink_id=permalink_id, status=str(status))

"""
#   ONE TIME used jsut to convert permalinks from ids to links
@application.route('/replace', methods=['GET', 'POST'])
@application.route('/replace/<permalink_id>', methods=['GET', 'POST'])
def replace(permalink_id=None):
    if(permalink_id):
        status, msg = sync(operation='replace', permalink_id=permalink_id)
    else:
        status, msg = sync(operation='replace')

    return render_template("request_sync.html", permalink_id=permalink_id, status=str(status))
"""


@application.route('/sync', methods=['GET', 'POST'])
@application.route('/sync/<permalink_id>', methods=['GET', 'POST'])
def request_sync(permalink_id=None):
    return render_template("request_sync.html", permalink_id=permalink_id)

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
