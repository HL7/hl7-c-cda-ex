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
