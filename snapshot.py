#!/usr/bin/env python2.7

import cv2
import sys
import os
import requests
from slacker import Slacker
import json

#config_file = sys.argv[1]
config_file = '/home/maria/PycharmProjects/SmartHome/git/internal_camera.yaml'
config_content = open(config_file)
config = json.load(config_content)

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

# Below code will capture the video frames and will sve it a folder (in current working directory)
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

#camera_ip = "192.168.1.108"
camera_ip = config.get("camera_ip", "")
#camera_url = "rtsp://admin:admin@{}/onvif1".format(camera_ip)
camera_url = config.get("camera_url", "").format(camera_ip)

slack_token = config.get("slack_token", "")
slack_channel = config.get("slack_channel", "")

def post_slack(text_msg):
    try:
        slack = Slacker(slack_token)

        slack.chat.post_message(slack_channel, text_msg)

    except:
        message = str(sys.exc_info())
        print (message)

def capture_snapshot():
    dirname = r""
    # video path
    # cap = cv2.VideoCapture("rtsp://admin:admin@192.168.1.102/onvif1", cv2.CAP_FFMPEG)
    cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)

    if cap.isOpened():
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        # The received "frame" will be saved. Or you can manipulate "frame" as per your needs.
        name = os.path.join(dirname, "internal.jpg")
        # print name
        cv2.imwrite(name, frame)

        my_file = {
            'file': ('internal.jpg', open('internal.jpg', 'rb'), 'gif')
        }

        payload = {
            "filename": "internal.jpg",
            "token": slack_token,
            "channels": [slack_channel],
        }

        r = requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)
        post_slack('Motion captured, image sent')

    cap.release()
    cv2.destroyAllWindows()




