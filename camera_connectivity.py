import os
import requests
import subprocess
import json
import sys

config_content = open("../config_files/config.yaml")
config = json.load(config_content)
slack_url = config.get("slack_url", "")


camera_statuses = open("../camera_statuses.yaml", "w")
#curr_camera_statuses = json.load(camera_statuses)

camera_statuses.write('{ "192.168.1.102": "online", "192.168.1.108": "online" ')
camera_statuses.close()


status = config.get("slack_url", "")


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
    camera_list = []
    camera_list.append('192.168.1.102')
    camera_list.append('192.168.1.108')

    for camera in camera_list:
        bashCommand = "telnet {}".format(camera)
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if 'Connection refused' in error:
            post_slack('camera {} is online'.format(camera),slack_url)
        else:
            if 'No route to host' in error:
                post_slack('ALERT: camera {} has been disconnected!'.format(camera), slack_url)
            else:
                post_slack('ALERT: unclear camera {} status! {}'.format(camera,error), slack_url)

except Exception as e:
    message = str(sys.exc_info())
    post_slack('camera {} status check have failed: {}'.format(camera,message),slack_url)