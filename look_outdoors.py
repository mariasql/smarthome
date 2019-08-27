#!/usr/bin/env python2.7

import cv2
import sys
import os
import requests
from slacker import Slacker
import json

#test comment

#config_file = sys.argv[1]

config_content = open("window_camera.yaml")
config = json.load(config_content)

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

# Below code will capture the video frames and will sve it a folder (in current working directory)
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

camera_ip = config.get("camera_ip", "")
camera_url = config.get("camera_url", "").format(camera_ip)

slack_url = config.get("slack_url", "")
slack_token = config.get("slack_token", "")
slack_channel = config.get("slack_channel", "")
to

def capture_snapshot(slack_token):
    dirname = r""
    # video path
    cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)

    if cap.isOpened():
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        # The received "frame" will be saved. Or you can manipulate "frame" as per your needs.
        name = os.path.join(dirname, "outdoor.jpg")
        # print name
        cv2.imwrite(name, frame)

        my_file = {
            'file': ('outdoor.jpg', open('outdoor.jpg', 'rb'), 'gif')
        }

        payload = {
            "filename": "outdoor.jpg",
            "token": slack_token,
            "channels": [slack_channel],
        }

        r = requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)

    cap.release()
    cv2.destroyAllWindows()


def post_slack(text_msg,slack_url):
    webhook_url = slack_url
    slack_data = {'text': text_msg}

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
    capture_snapshot(slack_token)
    post_slack('Image posted. Have a great day',slack_url)
except Exception as e:
    message = str(sys.exc_info())
    post_slack(message)
