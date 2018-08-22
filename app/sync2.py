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


def sync(operation='sync'):

    #   repo = git.Repo(folder)
    LOCAL_EXAMPLES_REPO_DIR = "./ccda_examples_repo"

    #   delete local repo if it already exists (left over from a previous sync operation)
    if os.path.isdir(LOCAL_EXAMPLES_REPO_DIR):
        shutil.rmtree(LOCAL_EXAMPLES_REPO_DIR)
    try:
        repo = git.Repo.clone_from(GIT_URL, LOCAL_EXAMPLES_REPO_DIR)
        repo.git.fetch()
        repo.git.reset("--hard", "origin/{}".format(GIT_BRANCH))
        repo.git.pull("origin", GIT_BRANCH)
        repo.git.checkout(GIT_BRANCH)
        return True, repo
    except Exception as e:
        return False, e