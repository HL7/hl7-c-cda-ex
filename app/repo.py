import os, re, urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, ipdb
import markdown2
from pygments import highlight
from pygments.lexers import XmlLexer, guess_lexer
from pygments.formatters import HtmlFormatter
import uuid
from slackbot import sc
from app.db import db, GIT_BRANCH, GIT_URL, GIT_COMMITTER_NAME, GIT_COMMITTER_EMAIL
from .sync2 import sync

folder = 'ccda_examples_repo'

def get_sections():
    sections = []
    for path,dirs,files in os.walk(folder):
        print("path: {} dir: {} ".format(path, dirs))
        dirs[:] = [d for d in dirs if not d[0] ==  '.' ]


        for filename in files:

            #   section folder
            if filename.lower() == "readme.md" and len(dirs) != 0 and path != folder:
                #   print os.path.join(path,filename)
                pth = os.path.join(re.sub(folder, '', path), filename)
                pth = pth.lstrip('/')
                with open(os.path.join(path,filename), 'rb') as readme:
                    description = readme.read()
                    description = description.decode('utf8').replace("##", "")
                    section_name = path.split(os.path.sep)[-1]
                    section = {
                        "name": section_name,
                        "description": description,
                        "slug": urllib.parse.quote(section_name),
                        "examples": []
                    }
                    sections.append(section)
    sections.decode('utf8').sort()
    return sections

def get_section(section_name):
    section = {'name': section_name, 'slug': urllib.parse.quote(section_name)}
    examples = []
    print(section_name)
    for path,dirs,files in os.walk(os.path.join(folder, section_name)):
        print("path: {} dir: {} ".format(path, dirs))
        dirs[:] = [d for d in dirs if not d[0] in ['.', section_name] ]

        for filename in files:

            #   section folder
            if filename.lower() == "readme.md" and path != os.path.join(folder, section_name): # and len(dirs) != 0:
                #   print os.path.join(path,filename)
                pth = os.path.join(re.sub(folder, '', path), filename)
                pth = pth.lstrip('/')
                with open(os.path.join(path,filename), 'rb') as readme:
                    content = readme.read()
                    description = content.replace("##", "")
                    example_name = path.split(os.path.sep)[-1]
                    example = {
                        "name": example_name,
                        "description": description,
                        "slug": urllib.parse.quote(example_name)
                    }
                    example['approval_status'] = get_approval_status(content)

                    examples.append(example)
    examples.sort()
    return section, examples

def get_example(section_name, example_name):
    section = {'name': section_name, 'slug': urllib.parse.quote(section_name)}
    readme = {'name': example_name, 'slug': urllib.parse.quote(example_name)}
    examples = []
    for path,dirs,files in os.walk(os.path.join(folder, section_name, example_name)):
        print("path: {} dir: {} ".format(path, dirs))
        dirs[:] = [d for d in dirs if not d[0] == '.']

        for filename in files:

            print(os.path.join(path,filename))
            pth = os.path.join(re.sub(folder, '', path), filename)
            pth = pth.lstrip('/')
            with open(os.path.join(path,filename), 'rb') as file:
                content = file.read()
                #   content = readme.replace("##", "")
                #   example_filename = path.split(os.path.sep)[-1]
                print("example_filename = {}".format(filename))
                github_url = "https://github.com/HL7/C-CDA-Examples/blob/master/{}/{}/{}".format(section_name, example_name, filename)
                example = {
                    "name": filename,
                    "github_url": github_url
                }


                if filename.lower() == 'readme.md' :
                    #   decoded_content = base64.b64decode(json_data['content'])
                    readme['content'] = markdown2.markdown(content)
                    readme['has_permalink'] = has_permalink(content)
                    readme['filename'] = filename

                elif filename.endswith('.xml'):

                    #   decoded_content = base64.b64decode(json_data['content'])
                    lexer = XmlLexer() #  guess_lexer(example['xml'])
                    style = HtmlFormatter(style='friendly').style
                    example['content'] = highlight(content, lexer, HtmlFormatter(full=True, style='colorful'))
                    examples.append(example)
                elif filename.endswith('.html'):

                    #   decoded_content = base64.b64decode(json_data['content'])
                    #   utf8_content = decoded_content.decode("utf8")
                    example['content'] = content
                    examples.append(example)
        return section, readme, examples

def get_file(section, example, filename):

    with open(os.path.join(folder,section,example,filename), 'rb') as file:
        content = file.read()
        return content

def search(query, status, onc_certified):
    results = []
    #   ipdb.set_trace()
    for path,dirs,files in os.walk(folder):
        print("path: {} dir: {} ".format(path, dirs))
        dirs[:] = [d for d in dirs if not d[0] ==  '.' ]

        for filename in files:

            #   section folder
            if filename.lower() == "readme.md" and len(dirs) == 0:
                #   print os.path.join(path,filename)
                pth = os.path.join(re.sub(folder, '', path), filename)
                pth = pth.lstrip('/')
                with open(os.path.join(path,filename), 'rb') as readme:
                    section_name = path.split(os.path.sep)[-2]
                    example_name = path.split(os.path.sep)[-1]
                    content = readme.read()
                    #   description = description.replace("##", "")
                    onc = "* ONC"

                    status_criteria = not status or (status and content.find("Approval Status: {}".format(status)) != -1 )
                    onc_certified_criteria = not onc_certified or (onc_certified and content.find(onc) != -1)
                    #   print "searching for {} in {}".format(query, example_name)
                    #   ipdb.set_trace()
                    search_criteria = content.find(query) != -1 or example_name.find(query) != -1
                    if search_criteria and status_criteria and onc_certified_criteria:
                        print("found  {} in {}".format(query, example_name))
                        section_name = path.split(os.path.sep)[-2]
                        example_name = path.split(os.path.sep)[-1]
                        results.append({
                            "section": section_name,
                            "example": example_name,
                            "approval_status": get_approval_status(content)
                        })
    results.sort()
    return results


def get_approval_status(content):
    if content.find('Approval Status: Withdrawn') != -1:
        return'Withdrawn'
    if content.find('Approval Status: Approved') != -1:
        return 'Approved'
    if content.find('Approval Status: Pending') != -1:
        return 'Pending'

def has_permalink(content):
    #   returns True if content has a permalink section already, False if it doesn't
    return content.find('Permalink') != -1

def generate_permalink(section, example, readme_filename):
    try:
        synced, repo = sync()
    except Exception as e:
        print(str(e))
        print('sync with repo failed')
        #   ipdb.set_trace()
        sc.api_call(
          "chat.postMessage",
          channel="hl7-notifications",
          text="uh oh: error doing the pre permalink generation sync with hl7 repo b {}".format(str(e))
        )
        return False, str(e)
    with open(os.path.join(folder,section,example, readme_filename), 'r+') as readme:

        content = readme.read()
        #   check if file has permalink
        if has_permalink(content):
            return False, "permalink exists already"

        #   ipdb.set_trace()
        permalink_id = str(uuid.uuid4())
        link = "http://cdasearch.hl7.org/examples/view/{}".format(permalink_id)
        markdown_link = "[{}]({})".format(link,link)
        new_permalink = "\n\n### Permalink \n\n* {}".format(markdown_link)
        print("new permalink is {}".format(link))
        #   append Permalink section to readme file
        readme.write(new_permalink)

    db.examples.insert_one({
        "section": section,
        "name": example,
        "PermalinkId": permalink_id,
        "Permalink": link
    })
    print("inserted into database")

    print("updating repo")
    reader = repo.config_reader()
    #repo.git.config(user_name="hl7bot")
    #repo.git.config(user_email='donotreply@hl7.org')
    try:
        with repo.config_writer() as writer:
            writer.set_value("user", "name", GIT_COMMITTER_NAME)
            writer.set_value("user", "email", GIT_COMMITTER_EMAIL)

        repo.git.add("-A")
        repo.git.commit(m="adding automagically generated permalink ids for new examples")
        repo.remotes.origin.push(refspec='{}:{}'.format(GIT_BRANCH,GIT_BRANCH))
        print("repo updated")
    except Exception as e:
        print("updating repo failed")
        #   ipdb.set_trace()
        sc.api_call(
          "chat.postMessage",
          channel="hl7-notifications",
          text="uh oh: error when committing back to hl7 repo {}".format(str(e))
        )
        return False, str(e)
    return True, 'success'
