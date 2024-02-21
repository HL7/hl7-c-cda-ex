### Update 02/21/2024 - Joshua Procious

So you want to update an app that is way out of date, cobbled together, and was only ever partially useful? ... Let's do it.

This whole investigation started off by "permalinks" not working any longer on cdasearch.hl7.org. They would just sit there and spin when clicked on.
Turns out that MongoDB extension (which was previously free on Heroku and where the previous MONGODB_URI pointed) went away. Heroku then automatically attempted to convert us to a Postgres free edition. I don't know if you've ever tried to migrate from MongoDB to Postgres, but it's not a one click process. So that is why permalinks weren't working, the Mongo Database went away.

I discovered that the HL7/hl7-c-cda-ex repo was never updated when Python conversion from 2 to 3 (2to3) took place now was the webhook properly set up. I spent a good deal of time just trying to get that repo to work before realizing.

Once I got a local clone of the active Heroku git stored hl7-c-cda-ex app (https://git.heroku.com/hl7-c-cda-examples.git) I was able to start updating.
This looks like: clone repo, cd repo, create virtual env python, install requirements.txt, working through dependency changes and mismatches along the way.
I used ChatGPT4 to help resolved dependencies that had changed since last update. Especially time saving for when a version reference style has changed (previously py2neo==0.59.1 now py2neo==2021.2.4)
In researching alternatives to our previously free MongoDB, I found that MongoDB Atlas allowed creating small free Databases (512MB). Since our information here is small and will scale extremely slowly, I created a free MongoDB Atlas DB ("hl7-c-cda-search") in the cloud for free at: https://account.mongodb.com/account/login You may log in with MONGODB_ATLAS_LOGIN_CREDS in Heroku config vars.
I updated the runtime.txt to be compatible with Heroku-22 stack. (as per: https://devcenter.heroku.com/articles/python-support#supported-runtimes)

Regarding Changes to the Python app:
  1. Updated standard syntax errors that were left over from the 2to3 Python conversion. Mainly around printing and some open as "rb" without encoding reference instead of "r" with encoding reference
  1. Updated Connection information to DB and committer information
  1. Added Logic to check for permalink ID and match it to _id in the Database
  1. Added Logic to not overwrite or create a new _id if one existed
  1. Removed Permalink Generation Ability from App
    1. Removed Git Sync Operation
  1. Commented-out "Generate Permalink Display" in templates/readme_examples.html to hide that button
  1. Added Print Statements to many files determine which code was actually being called in lack of a shockingly comment-free environment
    1. Commented these out on parse_met_data.py which is the only parsing file that is actually used with the removal of Permalink Generation
  1. Commented out code that was breaking Validation Location inserts into the DB
  1. Added /env and /ccda_examples_repo to .gitignore
  1. See git diff for full list of changes to the code

As I worked through the permalink generation, trying to preserve the ones that were present and likely linked out to external sites or Confluence, I found discrepancies in the CDA Examples repo Readme.md files for Permalinks and Validation Locations. I updated those to conform to the standard Readme.md.

TO GENERATE NEW PEMALINKS: This is now manual given our current climate and that historically this was overwriting Permalinks and saving them (ironic and not sure this ever worked). You should consult the MONGO DB using MongoDB Compass or similar and look at previous permalinks. Generate a new one using DB default creation or other tool of your choice and update the related Readme.md with "## Permalink" and then "* <url constructed with new permalink>" under that section in the https://github.com/HL7/C-CDA-Examples/ repository. Finally, to sync, go to https://cdasearch.hl7.org/sync and click "sync now".

Final notes: I have left the additional Config Vars in Heroku for Git operations and the code untouched in case someone ever takes on the task of rebuilding the pistons of this app. If you run this in a Windows 11 Environment for local testing (like I did as a below-novice programmer), you will likely need to remove the read-only flag that is automatically added to the local ccda_examples_repo folder which is created, on every time that you want to sync. 

# python/flask port of HL7 C-CDA Examples Heroku App

## Overall changes
The most significant change to the  foundation of the HL7 C-CDA Examples Heroku App is changing the original app from using ruby/rails to python/flask.  Throughout the documentation, I mention specific changes related to ruby/python.  Otherwise, the functionality of the app is entirely the same with the addition of the requested changes and fixes.
The original app is in the GitHub repo under the original_app branch.  The current version of the app in use in production is in the master branch


### Heroku Plugins
The app now uses mongodb instead of postgresdb therefore Heroku needs to be configured with a mongodb plugin as well.  Currently, the app is using the mlab mongodb plugin.

### Changes to Heroku Config Variables

| variable name | value                                             | description                                                                                           |
| ------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| APP_PORT      | 80                                                |                                                                                                       |
| APP_URI       | hl7-c-cda-examples.herokuapp.com                  |                                                                                                       |
| DATABASE_NAME | heroku_4zktbrkp                                   |                                                                                                       |
| GIT_BRANCH    | master                                            | branch of the C-CDA Examples repo to sync with                                                        |
| GIT_URL       | https://{TOKEN}@github.com/HL7/C-CDA-Examples.git | should include token for allowing deployment  from the Heroku instance without authenticating         |
| HEROKU        | 1                                                 | flag to use Heroku environment variables instead of config.ini file                                   |
| MONGODB_URI   | [see heroku app]                                  | mongo db connection uri, should be added automatically when mLab plug in is enabled on the heroku app |


The following are the old Heroku Config variables used by the original ruby on rails app that are no longer used:

- SECRET_KEY_BASE
- LANG
- DATABASE_URL
- RACK_ENV
- RAILS_ENV
- RAILS_SERVER_STATIC_FILES


### build pack

Whenever a Heroku app is deployed, Heroku uses “build packs” to install dependencies and configure the environments.  Because the new version of the app is built in python, the former `heroku/ruby` buildpack was replaced with the `heroku/python`  build pack.  The python build pack uses pip to install dependencies listed in the projects requirements.txt file.


### Automatic synchronization with Examples GitHub Repo
![alt text](https://raw.githubusercontent.com/schmoney/hl7-c-cda-ex/master/static/images/automagicPermalinks.png)

1. SDWG TF member* pushes updated examples to GitHub HL7/C-CDA-Examples repo
2. Commits to the GitHub Repo trigger a webhook to update the  Herokup app based on the latest commit to the master branch
3. The Heroku App checks each example to see if it has the Permalink ID.  
  1. Permalink ID’s are generated for examples that don’t have one and the new Permalinks are commited and pushed back to the GitHub Repo.  This commit triggers another call to the webhook (step 2)
4. Heroku App is updated with new examples including the Permalink IDs

NOTE: \*any GitHub user with write access to the HL7/C-CDA-Examples repo can push changes to the repo, not just SDWG Examples Task Force members.

In order for commits to the GitHub repo to trigger this synchronization process, the GitHub repo will need to have a webhook point to the following url endpoint: https://hl7-c-cda-examples.herokuapp.com/sync.  Do the following to set up the Webhook in GitHub:


1. sign in to GitHub as user with admin access to the C-CDA-Examples repo
2. Navigate to the C-CDA-Examples repo
3. Navigate to the Settings > Webhooks section
4. Click add webhook and provide the url endpoint mentioned above
5. Choose `application/json` as the *Content-type*
6. leave *Secret* blank
7. Choose `just push event` for the *Which events should trigger*


### Manual Synchronization with the Examples GitHub Repo

In order to manually update the Heroku App, simply visit the following url:
https://hl7-c-cda-examples.herokuapp.com/sync


### Other Future Considerations

#### Markdown formatting

Readme files don’t use MarkDown formatting for the headings.  For example, each heading contains the markdown heading markup ### instead of displaying as heading 3.  This is done consistently across all headings in all Readme files.  The impact is mostly cosmetic, instead of the Readme files appearing to be formatted, they contain the markup for each heading.  However, this app parses the Readme files whenever changes are made to the C-CDA Examples Repository.  

If in the future, contributors commit examples where the readme file does not follow this convention, this may not be parsed properly by the app.

#### Github repo and Heroku Repo
This app is deployed to heroku by pushing to the git repo hosted by Heroku.  Keep in mind that the Heroku git repo is separate from the Github repo.  While the Github repo is the official repo, the production app is running off of the latest code in the master branch of the Heroku repo.  Be sure to keep both repos in sync so that the official Github repo reflects the app in production hosted on Heroku.
