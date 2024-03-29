import os, ipdb, re, datetime, markdown2, urllib.request, urllib.parse, urllib.error
from git import Repo
from pygments import highlight
from pygments.lexers import XmlLexer, guess_lexer
from pygments.formatters import HtmlFormatter

from bson import ObjectId

folder = '../C-CDA-Examples'
#folder = '../ccda_examples_repo'

VALIDATOR_LOOKUP = {
    "https://sitenv.org/c-cda-validator": "SITE C-CDA Validator",
    "https://sitenv.org/sandbox-ccda/ccda-validator": "SITE C-CDA Validator"
}

from app.db import db, GIT_BRANCH, GIT_URL

#this lets us see when permalinks are processed in parse below
total_count_permalinks = 0

def get_name(section):
    #print("getting names", section)
    lines = section.split("\n\n")
    nme = lines[0].strip()
    if nme.startswith("Comment"):
        # ipdb.set_trace()
        pass
    name = lines[0].strip()
    try:
        colon = name.index(':')
        name = name[:colon]
    except:
        pass

    return name.split("\n")[0]


def process_section(doc, name, section):
    #print("start processing section", section)

    if section.strip().startswith(name): # not clear what this section maps to in the front end

        lines = section.split("\n")
        #   ipdb.set_trace()
        lines = [ l.replace('* ', '') for l in lines if l.startswith("*") ]

        #   get rid of remaining #
        name = name.strip()[1:] if name.startswith("#") else name.strip()
        name = name.strip() # catch any lingering white spaces i.e. "# Validaton" => " Validation" => "Validation"
        # make name safe for mongo
        name = name.replace(".", ' ')
        #print("name to be processed is: ", name)

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
                print("no status")
                pass

        '''
        if name == 'Validation location':
            # Check if the line starts with an expected format before proceeding
            if lines[0].startswith("CDA valid, no C-CDA rules exist"):
                link = None
                name = 'CDA valid, no C-CDA rules exist'
            elif lines[0].lower() in ['n/a', 'not applicable', 'tbd']:
                link = None
                name = 'N/A'
            else:
                try:
                    link = lines[0][lines[0].index('(')+1 : lines[0].index(')')]
                    name = VALIDATOR_LOOKUP[link]
                except Exception as e:
                    link = lines[0]
                    print(e)
                    #   ipdb.set_trace()
                if link in VALIDATOR_LOOKUP:
                    name = VALIDATOR_LOOKUP[link]
                else:
                    name = link

            doc['validator'] = {
                                "link": link,
                                "name": name
                                }
        '''

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
    #print("processing sections")
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
'''def process_readme(repo, section_name, example_name, data, xml_data, google_sheets_url, path, readme_filename, update_one_example_only=None):
    sections = data.split('##')
    doc = process_sections(example_name, sections)

    # Prepare document fields
    doc['section'] = section_name
    doc['name'] = example_name
    doc['readme'] = data
    doc['updated_on'] = datetime.datetime.now()

    if xml_data:
        doc['xml_data'] = xml_data
    if google_sheets_url:
        doc['google_sheets_url'] = google_sheets_url

    # Search for existing entry by permalink or example name and section
    search_criteria = {"$or": [{"Permalink": doc.get('Permalink')}, {"name": example_name, "section": section_name}]}
    existing_entry = db.examples.find_one(search_criteria)

    # Decide whether to insert a new document or update an existing one
    if existing_entry:
        # Update the existing document
        db.examples.update_one({"_id": ObjectId(existing_entry['_id'])}, {"$set": doc})
        print(f"Updated existing entry for {example_name} in section {section_name}.")
        should_commit = True
    else:
        # Insert a new document and add permalink if not present
        if 'Permalink' not in doc or not doc['Permalink']:
            # Generate and assign a new permalink here, if necessary
            permalink_id = str(db.examples.insert_one(doc).inserted_id)
            permalink = f"http://cdasearch.hl7.org/examples/view/{permalink_id}"
            db.examples.update_one({"_id": ObjectId(permalink_id)}, {"$set": {"Permalink": permalink}})
            print(f"Inserted new entry with permalink {permalink} for {example_name} in section {section_name}.")
        else:
            db.examples.insert_one(doc)
            print(f"Inserted new entry for {example_name} in section {section_name}.")
        should_commit = True

    # Commit changes to the repository if needed
    if should_commit:
        try:
            repo.git.add(A=True)
            repo.git.commit('-m', 'Automatically updated example entries.')
            repo.remotes.origin.push()
            print("Changes pushed to the repository.")
        except Exception as e:
            print(f"Failed to commit changes to the repository: {e}")

    return should_commit
'''

def process_readme(repo, section_name, example_name, data, xml_data, google_sheets_url, path, readme_filename, update_one_example_only=None):
    #print("processing readme function")
    #global reference to total_count_permalinks so we can access in this definition
    global total_count_permalinks

    #   add example links to readme BEFORE readme is parsed and saved to db
    if xml_data is None or google_sheets_url:
        added_links = False

    else:
        #print("checking for xml links 1")
        added_links = False
        #   ONETIME just to add xml links to readme's
        #   added_links = add_xml_links_to_readme(repo, path, section_name, example_name, readme_filename, xml_data)


    sections = data.split('##')
    doc = process_sections(example_name, sections)
    #print("post process xml links")
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
        #print("checking for xml links 2")
        doc['xml_data'] = xml_data
        #print("checking for xml links 3")
        # to do : look for filenames in xml_data[0][filename]
        #   added_links = add_xml_links_to_readme(repo, path, section_name, example_name, readme_filename, xml_data)


        # https://github.com/HL7/C-CDA-Examples/tree/master/Mental%20Status/Memory%20Impairment

    doc['updated_on'] = datetime.datetime.now()
    should_commit = False

    #if doc['name'] in ['Parent Document Replace Relationship']:
    #    ipdb.set_trace()
    #if added_links:
        # should_commit = True
    '''
    if 'Permalink' in doc and doc['Permalink'] != None:
        #   ipdb.set_trace()
        print("updating example {}.{} ({})".format(doc['section'], doc['name'], doc['Permalink']))
        result = db.examples.replace_one({"Permalink": str(doc['Permalink'])}, doc, upsert=True)
        #increment the permalink count by 1 and print to heroku log
        total_count_permalinks += 1
        print('total processed entries: ',total_count_permalinks)
    '''
    if 'Permalink' in doc and doc['Permalink']:
        # Find the position of the "]" character in the permalink
        end_pos = doc['Permalink'].find(']')
        if end_pos != -1:
            # Extract everything up to the "]" character
            extracted_part = doc['Permalink'][:end_pos]
            
            # Further processing to extract ID or perform other operations
            # For example, if you need to extract the ID after "/examples/view/"
            parts = extracted_part.split("/examples/view/")
            if len(parts) > 1:
                # Extracted ID from the permalink
                extracted_id = parts[1]
                
                # Convert the extracted ID to ObjectId if necessary
                # Note: Only do this if the extracted ID is meant to be an ObjectId
                try:
                    # Assuming extracted_id is meant to be a MongoDB ObjectId
                    permalink_id = ObjectId(extracted_id)
                except:
                    # If conversion fails or not needed, use extracted_id as is
                    permalink_id = extracted_id
                
                # Set the _id, permalink, and permalinkId
                doc['_id'] = permalink_id
                doc['Permalink'] = f"http://cdasearch.hl7.org/examples/view/{permalink_id}"
                doc['PermalinkId'] = str(permalink_id)
                
                # Use the extracted ID to check for existing entries or any other operations
                existing_entry = db.examples.find_one({"_id": permalink_id})
                if existing_entry:
                    # Update the existing entry with new data
                    print("about to update permalink")
                    db.examples.update_one({"_id": permalink_id}, {"$set": doc})
                    print(f"Updated existing entry with _id {permalink_id}")
                else:
                    #   add permalink to readme
                    result = db.examples.insert_one(doc)
                    permalink_id = str(result.inserted_id)
                    permalink = "http://cdasearch.hl7.org/examples/view/{}".format(permalink_id)

                    update_readme(repo, path, readme_filename, permalink)

                    doc['Permalink'] = permalink
                    #doc['PermalinkId'] = permalink
                    print("creating new permalink {}.{} for {}".format(doc['section'], doc['Permalink'], doc['name']))
                    #increment the permalink count by 1 and print to heroku log
                    total_count_permalinks += 1
                    print('total processed entries: ',total_count_permalinks)
                    #   result = db.examples.replace_one({"Permalink": str(doc['Permalink'])}, doc, upsert=True)
                    #   ipdb.set_trace()

                    query = {"_id": doc['_id']} #  TODO: change back to this
                    #   query = {"Permalink": permalink}
                    updates = {
                        "$set": { "Permalink": str(doc['Permalink']), "PermalinkId": str(permalink_id) }
                    }
                    #print("updates about to be updated:  ",updates)
                    #for section in sections:
                        #print("section as about to be updated (2): ", section)
                    update_result = db.examples.update_one(query, updates)
                    #   commit change to readme
                    should_commit = True
                    #   ipdb.set_trace()
                    #   push change to GitHub repo
            else:
                # Handle case where permalink does not contain the expected pattern
                print("Permalink format does not match expected pattern.")
        else:
            # Handle case where permalink does not contain "/examples/view/"
            print("Invalid Permalink format.", example_name)
    else:
        # Handle case where Permalink is not in doc or is None
        print("Permalink not found or is None.", example_name)
        
    if section_name.startswith('General'):
        #   ipdb.set_trace()
        print("{} id {} ".format(example_name, doc['Permalink']))
        #increment the permalink count by 1 and print to heroku log
        total_count_permalinks += 1
        print('total processed entries: ',total_count_permalinks)

    # return should_commit


#   loop through each section folder
def parse(repo, folder, update_one_example_only=None):
    #print("parsing")
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
                with open(os.path.join(path,filename), 'r', encoding='utf-8') as readme:
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
                        with open(os.path.join(path,xml_filename), 'r', encoding='utf-8') as xml:
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
                    with open(os.path.join(path,url_filename), 'r', encoding='utf-8') as urlfile:
                        urldata = urlfile.read()
                        lines = urldata.split("\n")
                        lines = [ l for l in lines if l.startswith("URL")]
                        if len(lines) == 1:
                            urlLineTokens = lines[0].split("=")
                            google_sheets_url = urlLineTokens[1] if len(urlLineTokens) >= 2 else "error"
                            #   url_data['url'] = url
                example_name = path.split(os.path.sep)[-1]
                with open(os.path.join(path,filename), 'r', encoding='utf-8') as readme:
                    data = readme.read()
                    #file_pth = os.path.join(path,filename)
                    #ipdb.set_trace()
                    #permalink_id = repo.git.hash_object(file_pth)
                    #   commit_new_id = process_readme(repo, section_name, example_name, data, example_xml, xml_filename, path, filename, update_one_example_only)
                    commit_new_id = process_readme(repo, section_name, example_name, data, xml_samples, google_sheets_url, path, filename, update_one_example_only=None)

                    #if commit_new_id:
                        # should_commit = True
    if should_commit:
        #print("updating repo")
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
    #print("updating readme")
    with open( os.path.join(path,readme_filename) , 'a+') as readme:
        readme.write(add_permalink(permalink))



def generate_permalink(repo, path, readme_filename, xml_filename):
    #print("generating permalink")
    xml_pth =  os.path.join(os.getcwd(), path, readme_filename)
    #ipdb.set_trace()
    #   get git blob hash of actual example xml file
    git_blob_hash = repo.git.hash_object(xml_pth)

    #   add Permalink to readme file
    with open( os.path.join(path,readme_filename) , 'a+') as readme:
        readme.write(add_permalink(git_blob_hash))

    return git_blob_hash

def add_permalink(id):
    print("adding permalink")
    return "\n\n###Permalink \n\n* %s" %id


def add_xml_links_to_readme(repo, path, section_name, example_name, readme_filename, xml_data):
    print("adding xml to readme")
    to_add = '\n\n###Links \n\n'
    for xml_link in xml_data:
        base_url = "https://github.com/HL7/C-CDA-Examples/tree/master"
        encoded_section = urllib.parse.quote(section_name)
        encoded_example_name = urllib.parse.quote(example_name)
        encoded_filename = urllib.parse.quote(xml_link['filename'])
        encoded_url = '{}/{}/{}/{}'.format(base_url, encoded_section, encoded_example_name, encoded_filename)
        to_add += "* [{}]({})\n".format(xml_link['filename'], encoded_url)
        print("generating link to add to example readme file - {}".format(encoded_url))
    with open( os.path.join(path,readme_filename) , 'a+') as readme:
        readme.write(to_add)
    return True

    #   https://github.com/schmoney/C-CDA-Examples/blob/master/Allergies/Allergy%20to%20cat%20hair/Allergy%20to%20specific%20substance%20cat%20hair(C-CDA2.1).xml
    #   https://github.com/HL7/C-CDA-Examples/tree/master/Allergies/Allergy+to+specific+substance+cat+hair%28C-CDA2.1%29.xml
    #   https://github.com/HL7/C-CDA-Examples/tree/master/Allergies/Allergy%20to%20cat%20hair/Allergy%20to%20specific%20substance%20cat%20hair%28C-CDA2.1%29.xml
