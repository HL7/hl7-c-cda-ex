import os, ipdb, re, datetime, markdown2
from git import Repo

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
                ipdb.set_trace()

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
        if name == 'Permalink' and doc[name] == []:
            #   set to None so that permalink gets generated later
            doc[name] = None

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


def process_readme(repo, section_name, example_name, data, example_xml, xml_filename, path, readme_filename, update_one_example_only):
    sections = data.split('##')
    doc = process_sections(example_name, sections)

    #   check if it's just this one example or all examples
    if update_one_example_only and 'Permalink' in doc and doc['Permalink'] != update_one_example_only:
        return False

    doc['section'] = section_name
    doc['name'] = example_name
    doc['xml'] = example_xml
    doc['xml_filename'] = xml_filename
    #   if no xml, then assume it's just a comment that links to the google doc
    if example_xml is None:
        #   convert markdown to html with link to google doc
        doc['google_sheets_url'] = markdown2.markdown(doc['Comments'])
    doc['updated_on'] = datetime.datetime.now()
    should_commit = False
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
        result = db.examples.replace_one({"_id": doc['Permalink']}, doc, upsert=True)
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
                if len(xml_files) != 1:
                    xml_filename = None
                    example_xml = None

                else:
                    xml_filename = xml_files[0]
                    #   print os.path.join(path,filename)
                    pth = os.path.join(re.sub(folder, '', path), filename)
                    pth = pth.lstrip('/')

                    example_xml = ''
                    with open(os.path.join(path,xml_filename), 'rU') as xml:
                        example_xml = xml.read()

                """
                url_files =  [ _file for _file in files if _file.lower().endswith(".url") ]
                if len(url_files) != 1:
                    pass
                else:
                    url_filename = url_files[0]
                    example_xml = ''
                    with open(os.path.join(path,url_filename), 'rU') as urlfile:
                        urldata = urlfile.read()
                        lines = urldata.split("\n")
                        lines = [ l for l in lines if l.startswith("URL")]
                """
                example_name = path.split(os.path.sep)[-1]
                with open(os.path.join(path,filename), 'rU') as readme:
                    data = readme.read()
                    #file_pth = os.path.join(path,filename)
                    #ipdb.set_trace()
                    #permalink_id = repo.git.hash_object(file_pth)
                    commit_new_id = process_readme(repo, section_name, example_name, data, example_xml, xml_filename, path, filename, update_one_example_only)

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
