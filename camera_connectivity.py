import os
import requests
import subprocess
import json

config_content = open("../config_files/config.yaml")
config = json.load(config_content)
slack_url = config.get("slack_url", "")

def post_slack(text_msg,slack_url):
    webhook_url = slack_url
    slack_data = {'text': "{}".format(text_msg)}

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


try:
    result = subprocess.run(['telnet 192.168.1.102', '-l'], stdout=subprocess.PIPE)
    post_slack(result,slack_url)