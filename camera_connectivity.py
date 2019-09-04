import os
import requests
import subprocess
import json
import sys

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
    bashCommand = "telnet 192.168.1.102"
    result=subprocess.run([bashCommand, '-l'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    post_slack('camera status: {}'.format(result),slack_url)
except Exception as e:
    message = str(sys.exc_info())
    post_slack('camera status check have failed: {}'.format(message),slack_url)