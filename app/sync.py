#!flask/bin/python
from app.db import db
import os.path
import git
import ipdb
import git
import shutil
from permalinks import parse
from replace_permalinks import replace_permalinks
from db import GIT_URL, GIT_BRANCH


def sync(operation='sync', permalink_id=None):

    #   repo = git.Repo(folder)
    LOCAL_EXAMPLES_REPO_DIR = "./ccda_examples_repo"

    #   delete local repo if it already exists (left over from a previous sync operation)
    if os.path.isdir(LOCAL_EXAMPLES_REPO_DIR):
        shutil.rmtree(LOCAL_EXAMPLES_REPO_DIR)

    repo = git.Repo.clone_from(GIT_URL, LOCAL_EXAMPLES_REPO_DIR)
    repo.git.fetch()
    repo.git.reset("--hard", "origin/{}".format(GIT_BRANCH))
    repo.git.pull("origin", GIT_BRANCH)
    repo.git.checkout(GIT_BRANCH)
    print GIT_BRANCH
    try:
        if operation == 'sync':
            should_delete = parse(repo, LOCAL_EXAMPLES_REPO_DIR, permalink_id)
        else:
            print "replacing in stead of normal sync"
            should_delete = replace_permalinks(repo, LOCAL_EXAMPLES_REPO_DIR, permalink_id)

        #   delete local repo afterwards
        if should_delete:
            #   ipdb.set_trace()
            shutil.rmtree(LOCAL_EXAMPLES_REPO_DIR)

        basedir = os.path.abspath(os.path.dirname(__file__))

        if not permalink_id:
            sections = db.sections.find().count()
            examples = db.examples.find().count()
            return True, "loaded {} sections and {} examples".format(sections, examples)
        else:
            return True, "reloaded example {}".format(permalink_id)
    except Exception as e:
        ipdb.set_trace()
        return False, str(e)
