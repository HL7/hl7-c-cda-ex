import os, ipdb, re, datetime, markdown2, urllib
from git import Repo
from pygments import highlight
from pygments.lexers import XmlLexer, guess_lexer
from pygments.formatters import HtmlFormatter
from slackbot import sc

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
        #   ipdb.set_trace()
        pass
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

        """
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
        """

        #   check if Permalink section is blank
        try:
            if name == 'Permalink' and 'Permalink' in doc and isinstance(doc[name], list) and len(doc[name]) == 0: # doc[name] == []:
                #   set to None so that permalink gets generated later
                #   ipdb.set_trace()
                doc[name] = None

        except Exception as e:
            print str(e)
            ipdb.set_trace()


def process_sections(example_name, sections):
    doc = {}
    for section in sections:
        if section != '':
            name = get_name(section)
            try:
                process_section(doc,name, section)
            except Exception as e:
                print str(e)
                ipdb.set_trace()

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
def process_readme(repo, section_name, example_name, data, path, readme_filename, update_one_example_only):

    sections = data.split('##')
    doc = process_sections(example_name, sections)

    #   check if it's just this one example or all examples
    if update_one_example_only and 'Permalink' in doc and doc['Permalink'] != update_one_example_only:
        return False

    doc['section'] = section_name
    doc['name'] = example_name
    doc['readme'] = data
    should_commit = False


    print "checking {}".format(example_name)
    #   return False
    if 'Permalink' in doc and doc['Permalink'] != None:
        pass
    else:
        #   ipdb.set_trace()
        #   add permalink to readme
        result = db.examples.insert_one(doc)
        _id = result.inserted_id
        permalink = str(_id)

        new_permalink, new_readme_contents = update_readme(repo, path, readme_filename, permalink)

        #doc['Permalink'] = new_permalink
        #doc['PermalinkId'] = permalink
        print "creating new permalink {}.{} for {}".format(doc['section'], permalink, doc['name'])
        #   result = db.examples.replace_one({"Permalink": str(doc['Permalink'])}, doc, upsert=True)
        #   ipdb.set_trace()

        query = {"_id": _id} #  TODO: change back to this
        #   query = {"Permalink": permalink}
        set_updates = {
            "Permalink": new_permalink,
            "PermalinkId": permalink,
            "readme": new_readme_contents,
            "updated_on": datetime.datetime.now()
        }
        updates = {
            "$set": set_updates
        }


        update_result = db.examples.update_one(query, updates)
        #   commit change to readme
        should_commit = True
        #   push change to GitHub repo

    return should_commit

#   loop through each section folder
def parse(repo, folder, update_one_example_only):
    should_commit = False
    for path,dirs,files in os.walk(folder):
        #print "path: {} dir: {} ".format(path, dirs)
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
                    """
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
                    """
            example_name = path.split(os.path.sep)[-1]
            #   actual example folder
            if filename.lower() == "readme.md" and len(dirs) == 0:
                with open(os.path.join(path,filename), 'rU') as readme:
                    #print os.path.join(path,filename)
                    data = readme.read()
                    commit_new_id = process_readme(repo, section_name, example_name, data, path, filename, update_one_example_only)
                    if commit_new_id:
                        print "should be committing"
                        should_commit = True
    if should_commit:
        print "updating repo"
        reader = repo.config_reader()
        #repo.git.config(user_name="hl7bot")
        #repo.git.config(user_email='donotreply@hl7.org')
        try:
            with repo.config_writer() as writer:
                writer.set_value("user", "name", "Chris Millet")
                writer.set_value("user", "email", "chris@thelazycompany.com")

            repo.git.add("-A")
            repo.git.commit(m="adding automagically generated permalink ids for new examples")
            repo.remotes.origin.push(refspec='{}:{}'.format(GIT_BRANCH,GIT_BRANCH))
            sc.api_call(
              "chat.postMessage",
              channel="hl7-notifications",
              text="permalink generated successfully, you may want to double check tho".format(str(e))
            )
        except Exception as e:
            sc.api_call(
              "chat.postMessage",
              channel="hl7-notifications",
              text="uh oh: error when committing back to hl7 repo {}".format(str(e))
            )
        return should_commit


def update_readme(repo, path, readme_filename, permalink):

    link = "http://cdasearch.hl7.org/examples/view/{}".format(permalink)
    markdown_link = "[{}]({})".format(link,link)
    new_permalink = "\n\n### Permalink \n\n* {}".format(markdown_link)
    #   append Permalink section to readme file
    with open( os.path.join(path,readme_filename) , 'a+') as readme:
        readme.write(new_permalink)

    #   get updated readme content
    with open( os.path.join(path,readme_filename) , 'r') as readme:
        new_text = readme.read()

    #   return Permalink and updated readme content
    return markdown_link, new_text
