import slack
import os

slack_token = os.environ["SLACK_API_TOKEN"]
sc = slack.RTMClient(token=slack_token)
