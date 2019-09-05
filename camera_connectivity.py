import requests
import subprocess
import json
import sys

config_content = open("../config_files/config.yaml")
config = json.load(config_content)
slack_url = config.get("slack_url", "")

#file initialization#
camera_statuses = open("../camera_statuses.yaml", "w")
new_status = '{"192.198.1.102": "unknown", "192.168.1.108": "unknown"}'
camera_statuses.write(new_status)
camera_statuses.close()

camera_statuses = open("../camera_statuses.yaml","r")
prev_camera_statuses = json.load(camera_statuses)
camera_statuses.close()

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
    new_status = {"192.168.1.102": "unknown", "192.168.1.108": "unknown"}

    for camera in camera_list:
        bashCommand = "telnet {}".format(camera)
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        prev_status = prev_camera_statuses.get(camera, "")

        if 'Connection refused' in error:
            if 'online' not in prev_status:
                post_slack('ALERT: camera {} is back online!'.format(camera), slack_url)
            new_status[camera] = "online"
            #post_slack('Camera statuses: {}'.format(str(new_status)), slack_url)

        else:
            if 'No route to host' in error:
                if 'offline' not in prev_status:
                    post_slack('ALERT: camera {} has been disconnected!'.format(camera), slack_url)
                new_status[camera] = "offline"
                #post_slack('Camera statuses: {}'.format(str(new_status)), slack_url)

            else:
                if 'unknown' not in prev_status:
                    post_slack('ALERT: unclear camera {} status! {}'.format(camera,error), slack_url)
                    new_status[camera] = "unknown"

    post_slack('Camera statuses: {}'.format(str(new_status)), slack_url)

    with open('../camera_statuses.yaml', 'w') as f:
        json.dump(new_status, f)

except Exception as e:
    message = str(sys.exc_info())
    post_slack('camera {} status check have failed: {}'.format(camera, message), slack_url)