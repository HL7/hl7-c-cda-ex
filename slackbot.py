import slack
import os

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)
