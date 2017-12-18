import os, ipdb, re, datetime, markdown2, urllib
from git import Repo
from pygments import highlight
from pygments.lexers import XmlLexer, guess_lexer
from pygments.formatters import HtmlFormatter

folder = '../C-CDA-Examples'
#folder = '../ccda_examples_repo'

VALIDATOR_LOOKUP = {
    "https://sitenv.org/c-cda-validator": "SITE C-CDA Validator",
    "https://sitenv.org/sandbox-ccda/ccda-validator": "SITE C-CDA Validator"
}

from app.db import db, GIT_BRANCH, GIT_URL

def get_name(section):
    lines = section.split("\n\n")
    nme = lines[0].strip()
    if nme.startswith("Comment"):
        ipdb.set_trace()
    name = lines[0].strip()
    try:
        colon = name.index(':')
        name = name[:colon]
    except:
        pass

    return name.split("\n")[0]


def process_section(doc, name, section):

    if section.strip().startswith(name): # not clear what this section maps to in the front end

        lines = section.split("\n")
        #   ipdb.set_trace()
        lines = [ l.replace('* ', '') for l in lines if l.startswith("*") ]

        #   get rid of remaining #
        name = name.strip()[1:] if name.startswith("#") else name.strip()
        name = name.strip() # catch any lingering white spaces i.e. "# Validaton" => " Validation" => "Validation"
        # make name safe for mongo
        name = name.replace(".", ' ')

        #   update Permalink field to just be the id, otherwise list of bulleted items
        isStr = name in ['Permalink', 'Comments', 'Custodian', 'Reference to full CDA sample', 'Certification']

        #if name.startswith('# Approval Status') or name.endswith(' Approval Status'):
        #    ipdb.set_trace()

        #if 'Approval Status' in [name, name2] and name != name2:
        #    ipdb.set_trace()

        if name == 'Approval Status':
            doc['approval']  = lines[0].split(":")[1].strip()
            if doc['approval'] in ['', None]:
                # ipdb.set_trace()
                print "no status"
                pass

        if name == 'Validation location':
            if lines[0].startswith("CDA valid, no C-CDA rules exist"):
                link = None
                name = 'CDA valid, no C-CDA rules exist'
            elif lines[0].lower() in ['n/a', 'not applicable']:
                link = None
                name = 'N/A'
            else:
                try:
                    link = lines[0][lines[0].index('(')+1 : lines[0].index(')')]
                    name = VALIDATOR_LOOKUP[link]
                except Exception as e:
                    link = lines[0]
                    #   print e
                    #   ipdb.set_trace()
                if link in VALIDATOR_LOOKUP:
                    name = VALIDATOR_LOOKUP[link]
                else:
                    name = link

            doc['validator'] = {
                                "link": link,
                                "name": name
                                }

        doc[name] = lines[0] if isStr and len(lines) == 1  else lines

        #   check if Permalink section is blank
        if name == 'Permalink' and isinstance(doc[name], list) and len(doc[name]) == 0: # doc[name] == []:
            #   set to None so that permalink gets generated later
            #   ipdb.set_trace()
            doc[name] = None

        #if 'name' in doc and doc['name'] in ['Parent Document Replace Relationship']:
        #    ipdb.set_trace()

        #if doc[name] == 'Multiple Patient Identifiers':
        #    ipdb.set_trace()

def process_sections(example_name, sections):
    doc = {}
    for section in sections:
        if section != '':
            name = get_name(section)

            process_section(doc,name, section)

            #   ipdb.set_trace()
            """
            if section.startswith("Approval Status"):
                lines = section.split("\n")
                lines = [ l for l in lines if l.startswith("*")]
                doc['Approval Status'] = lines
            if section.startswith("#C-CDA 2.1 Example"): # not clear what this section maps to in the front end
                lines = section.split("\n")
                lines = [ l for l in lines if l.startswith("*")]
                doc['C-CDA 2.1 Example'] = lines
            """
    return doc


#   def process_readme(repo, section_name, example_name, data, example_xml, xml_filename, path, readme_filename, update_one_example_only):
def process_readme(repo, section_name, example_name, data, xml_data, google_sheets_url, path, readme_filename, update_one_example_only):

    #   add example links to readme BEFORE readme is parsed and saved to db
    if xml_data is None or google_sheets_url:
        added_links = False
        pass
    else:
        print "checking for xml links"
        #   added_links = add_xml_links_to_readme(repo, path, section_name, example_name, readme_filename, xml_data)


    sections = data.split('##')
    doc = process_sections(example_name, sections)

    #   check if it's just this one example or all examples
    if update_one_example_only and 'Permalink' in doc and doc['Permalink'] != update_one_example_only:
        return False

    doc['section'] = section_name
    doc['name'] = example_name
    doc['readme'] = data

    """
    doc['xml'] = example_xml
    doc['xml_filename'] = xml_filename
    #   if no xml, then assume it's just a comment that links to the google doc
    if example_xml is None:
        #   convert markdown to html with link to google doc
        doc['google_sheets_url'] = markdown2.markdown(doc['Comments'])
    """
    #   ipdb.set_trace()

    if xml_data is None or google_sheets_url:
        doc['google_sheets_url'] = google_sheets_url #  markdown2.markdown(doc['Comments'])
    else:
        print "checking for xml links"
        doc['xml_data'] = xml_data
        # TODO: look for filenames in xml_data[0][filename]
        #   added_links = add_xml_links_to_readme(repo, path, section_name, example_name, readme_filename, xml_data)


        # https://github.com/HL7/C-CDA-Examples/tree/master/Mental%20Status/Memory%20Impairment

    doc['updated_on'] = datetime.datetime.now()
    should_commit = False

    #if doc['name'] in ['Parent Document Replace Relationship']:
    #    ipdb.set_trace()
    if added_links:
        should_commit = True

    if 'Permalink' in doc and doc['Permalink'] != None:
        print "updating example {}.{} ({})".format(doc['section'], doc['name'], doc['Permalink'])
        result = db.examples.replace_one({"Permalink": str(doc['Permalink'])}, doc, upsert=True)
        #   ipdb.set_trace()
    else:
        #   add permalink to readme
        result = db.examples.insert_one(doc)
        permalink = str(result.inserted_id)
        update_readme(repo, path, readme_filename, permalink)
        #   permalink = generate_permalink(repo, path, readme_filename, xml_filename)
        doc['Permalink'] = permalink
        print "creating new permalink {}.{} for {}".format(doc['section'], doc['Permalink'], doc['name'])
        #   result = db.examples.replace_one({"Permalink": str(doc['Permalink'])}, doc, upsert=True)
        update_result = db.examples.update_one({
            "_id": doc['_id']
        }, {
            "$set": {"Permalink": str(doc['Permalink'])}
        })
        #   commit change to readme
        should_commit = True
        #   ipdb.set_trace()
        #   push change to GitHub repo
    if section_name.startswith('General'):
        #   ipdb.set_trace()
        print "{} id {} ".format(example_name, doc['Permalink'])

    return should_commit

#   loop through each section folder
def parse(repo, folder, update_one_example_only):
    should_commit = False
    for path,dirs,files in os.walk(folder):
        #   print "path: {} dir: {} "
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for filename in files:
            #   section folder
            if filename.lower() == "readme.md" and len(dirs) != 0:
                #   print os.path.join(path,filename)
                pth = os.path.join(re.sub(folder, '', path), filename)
                pth = pth.lstrip('/')
                with open(os.path.join(path,filename), 'rb') as readme:
                    description = readme.read()
                    description = description.replace("##", "")
                    section_name = path.split(os.path.sep)[-1]

                    #   ipdb.set_trace()
                    if section_name not in  ['C-CDA-Examples', 'ccda_examples_repo']:
                        db.sections.update_one(
                            {"name": section_name},
                            {"$set":
                                {
                                    "name": section_name,
                                    "description": description
                                }
                            },
                            upsert=True
                        )

            #   actual example folder
            if filename.lower() == "readme.md" and dirs == []:
                #   get the xml file for the example
                xml_files =  [ _file for _file in files if _file.lower().endswith(".xml") ]
                if len(xml_files) == 0:
                    xml_filename = None
                    example_xml = None

                else:
                    xml_samples = []
                    for xml_file in xml_files:
                        xml_data = {"filename": '', "xml": '', 'formatted_xml': ''}
                        #   xml_filename = xml_files[0]
                        xml_filename = xml_file
                        #   print os.path.join(path,filename)
                        pth = os.path.join(re.sub(folder, '', path), filename)
                        pth = pth.lstrip('/')

                        example_xml = ''
                        with open(os.path.join(path,xml_filename), 'rU') as xml:
                            example_xml = xml.read()
                            xml_data['filename'] = xml_filename
                            xml_data["xml"] = example_xml
                            lexer = XmlLexer() #  guess_lexer(example['xml'])
                            style = HtmlFormatter(style='friendly').style
                            #   ipdb.set_trace()
                            formatted_xml = highlight(example_xml, lexer, HtmlFormatter(full=True, style='colorful'))
                            xml_data['formatted_xml'] = formatted_xml
                        xml_samples.append(xml_data)


                url_files =  [ _file for _file in files if _file.lower().endswith(".url") ]
                if len(url_files) != 1:
                    google_sheets_url=None
                else:
                    url_filename = url_files[0]
                    example_xml = ''
                    with open(os.path.join(path,url_filename), 'rU') as urlfile:
                        urldata = urlfile.read()
                        lines = urldata.split("\n")
                        lines = [ l for l in lines if l.startswith("URL")]
                        if len(lines) == 1:
                            urlLineTokens = lines[0].split("=")
                            google_sheets_url = urlLineTokens[1] if len(urlLineTokens) >= 2 else "error"
                            #   url_data['url'] = url
                example_name = path.split(os.path.sep)[-1]
                with open(os.path.join(path,filename), 'rU') as readme:
                    data = readme.read()
                    #file_pth = os.path.join(path,filename)
                    #ipdb.set_trace()
                    #permalink_id = repo.git.hash_object(file_pth)
                    #   commit_new_id = process_readme(repo, section_name, example_name, data, example_xml, xml_filename, path, filename, update_one_example_only)
                    commit_new_id = process_readme(repo, section_name, example_name, data, xml_samples, google_sheets_url, path, filename, update_one_example_only)

                    if commit_new_id:
                        should_commit = True
    if should_commit:
        print "updating repo"
        reader = repo.config_reader()
        #repo.git.config(user_name="hl7bot")
        #repo.git.config(user_email='donotreply@hl7.org')
        with repo.config_writer() as writer:
            writer.set_value("user", "name", "Chris Millet")
            writer.set_value("user", "email", "chris@thelazycompany.com")

        repo.git.add("-A")
        repo.git.commit(m="adding automagically generated permalink ids for new examples")
        repo.remotes.origin.push(refspec='master:master')
        return should_commit


def update_readme(repo, path, readme_filename, permalink):
    with open( os.path.join(path,readme_filename) , 'a+') as readme:
        readme.write(add_permalink(permalink))

def generate_permalink(repo, path, readme_filename, xml_filename):
    xml_pth =  os.path.join(os.getcwd(), path, readme_filename)
    #ipdb.set_trace()
    #   get git blob hash of actual example xml file
    git_blob_hash = repo.git.hash_object(xml_pth)

    #   add Permalink to readme file
    with open( os.path.join(path,readme_filename) , 'a+') as readme:
        readme.write(add_permalink(git_blob_hash))

    return git_blob_hash

def add_permalink(id):
    return "\n\n###Permalink \n\n* %s" %id


def add_xml_links_to_readme(repo, path, section_name, example_name, readme_filename, xml_data):
    to_add = '\n\n###Links \n\n'
    for xml_link in xml_data:
        base_url = "https://github.com/HL7/C-CDA-Examples/tree/master"
        encoded_section = urllib.quote(section_name)
        encoded_example_name = urllib.quote(example_name)
        encoded_filename = urllib.quote(xml_link['filename'])
        encoded_url = '{}/{}/{}/{}'.format(base_url, encoded_section, encoded_example_name, encoded_filename)
        to_add += "* [{}]({})\n".format(xml_link['filename'], encoded_url)
        print "generating link to add to example readme file - {}".format(encoded_url)
    with open( os.path.join(path,readme_filename) , 'a+') as readme:
        readme.write(to_add)
    return True

    #   https://github.com/schmoney/C-CDA-Examples/blob/master/Allergies/Allergy%20to%20cat%20hair/Allergy%20to%20specific%20substance%20cat%20hair(C-CDA2.1).xml
    #   https://github.com/HL7/C-CDA-Examples/tree/master/Allergies/Allergy+to+specific+substance+cat+hair%28C-CDA2.1%29.xml
    #   https://github.com/HL7/C-CDA-Examples/tree/master/Allergies/Allergy%20to%20cat%20hair/Allergy%20to%20specific%20substance%20cat%20hair%28C-CDA2.1%29.xml
