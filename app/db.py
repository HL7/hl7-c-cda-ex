import configparser
import os
from pymongo import MongoClient

config = configparser.ConfigParser()
config.read('app/config.ini')

if os.environ.get("HEROKU"):
    uri = os.environ.get("MONGODB_URI")
    database = os.environ.get("DATABASE_NAME")
    client = MongoClient(uri)
    GIT_URL = os.environ.get("GIT_URL")
    GIT_BRANCH = os.environ.get("GIT_BRANCH")
    GIT_COMMITTER_NAME = os.environ.get('GIT_COMMITTER_NAME')
    GIT_COMMITTER_EMAIL = os.environ.get('GIT_COMMITTER_EMAIL')
    #   GIT_SSH_KEY = os.environ.get("GIT_SSH_KEY")
else:
    
    '''
    #database = 'ccdaExamples'
    #client = MongoClient('localhost', 27017)

    #test
    database = 'heroku_brpn0kqd'
    client = MongoClient("mongodb://heroku_brpn0kqd:ji373v99tdvndpb3ccpvhg0sqe@ds155091.mlab.com:55091/heroku_brpn0kqd")
    GIT_URL = "https://github.com/schmoney/C-CDA-Examples.git"
    #   GIT_URL = "https://github.com/brettmarquard/C-CDA-Examples.git"
    #GIT_BRANCH = 'permalinksHashObject'
    GIT_BRANCH = 'permalink-gentest'
    GIT_SSH_KEY = ''
    GIT_COMMITTER_NAME = os.environ.get('GIT_COMMITTER_NAME')
    GIT_COMMITTER_EMAIL = os.environ.get('GIT_COMMITTER_EMAIL')

    '''
    ###
    # production
    #database = 'heroku_4zktbrkp'
    #client = MongoClient("mongodb://heroku_4zktbrkp:p6tt3tvn0fv1do77c70ip17ve5@ds127982.mlab.com:27982/heroku_4zktbrkp")
    database = 'hl7-c-cda-search'
    client = MongoClient("MONGODB_URI")
    GIT_URL = "https://github.com/HL7/C-CDA-Examples.git"
    #GIT_BRANCH = 'permalinksHashObject'
    GIT_BRANCH = 'master'
    GIT_SSH_KEY = ''
    GIT_COMMITTER_NAME = os.environ.get('GIT_COMMITTER_NAME')
    GIT_COMMITTER_EMAIL = os.environ.get('GIT_COMMITTER_EMAIL')
    ###


db = client[database]
