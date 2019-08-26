#!/usr/bin/env python2.7

import broadlink
import os
import cv2
from datetime import datetime, timedelta
import time
import logging
from logging.handlers import RotatingFileHandler
from slacker import Slacker
import requests
import sys
import json

config_content = open("config.yaml")
config = json.load(config_content)

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

camera_ip = config.get("camera_ip", "")
camera_url = config.get("camera_url", "").format(camera_ip)
slack_token = config.get("slack_token", "")
slack_channel = config.get("slack_channel", "")
minipc_ip = config.get("minipc_ip", "")
host_ip = config.get("host_ip", "")

image_title = 'rec_frame.jpg'

def capture_snapshot(camera_url,image_title,slack_token,slack_channel):
    dirname = r""
    # video path
    cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)

    if cap.isOpened():
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        # The received "frame" will be saved. Or you can manipulate "frame" as per your needs.
        name = os.path.join(dirname, image_title)
        #print name
        cv2.imwrite(name, frame)


        my_file = {
            'file': (image_title, open(image_title, 'rb'), 'gif')
        }

        payload = {
            "filename": image_title,
            "token": slack_token,
            "channels": [slack_channel],
        }

        try:
            r = requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)
        except:
            message = str(sys.exc_info())
            post_slack(message)

    cap.release()

    cv2.destroyAllWindows()


logfilename = r"smarthome.log"
logfile = open(logfilename, 'a')

def post_slack(text_msg,slack_token,slack_channel):
    try:
        slack = Slacker(slack_token)

        slack.chat.post_message(slack_channel, text_msg)

    except Exception as exc:
        exception = str(exc)
        print ("Error posting to Slack, {}".format(exception))
        print (text_msg)

def setlogging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  - %(message)s',
                        filename=logfilename)
    logging.handlers.RotatingFileHandler(filename=logfilename, maxBytes=10240, backupCount=5)
    stderrLogger = logging.StreamHandler()
    stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logging.getLogger().addHandler(stderrLogger)
    # disable urlib client info logging
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


setlogging()



devices = broadlink.S1C(host=(host_ip,80), mac="B4:43:0D:FE:E2:1F") # Change to your S1C MAC an IP

devices.auth()

logging.info(devices)

sens = devices.get_sensors_status()
old = sens

for i, se in enumerate(sens['sensors']):
    txt = 'Name:{}, status:{}, type: {}'.format(se['name'],se['status'],se['type'])
    post_slack(txt,slack_token,slack_channel)

while 1:
    try:
        sens = devices.get_sensors_status()
        for i, se in enumerate(sens['sensors']):
            if se['status'] != old['sensors'][i]['status']:
                sName = se['name']
                sType = se['type']
                if sType == "Door Sensor":
                    if str(se['status']) == "0" or str(se['status']) == "128":
                        txt = time.ctime() + ': Door closed ( status {} )'.format(str(se['status']))
                        logging.info(txt)
                        post_slack(txt,slack_token,slack_channel)
                    elif str(se['status']) == "16" or str(se['status']) == "144":
                        txt = time.ctime() + ': Door opened ( status {})'.format(str(se['status']))
                        logging.info(txt)
                        post_slack(txt,slack_token,slack_channel)

                    elif str(se['status']) == "48":
                        txt = time.ctime() + ':Door tampered ( status ' + str(se['status']) + ')'
                        logging.info(txt)
                        post_slack(txt,slack_token,slack_channel)

                elif sType == 'Motion Sensor' and str(se['status']) == "0" or sType == "Motion Sensor" and str(se['status']) == "32" or sType == "Motion Sensor" and str(se['status']) == "128":
                    txt = time.ctime() + ": No Motion: " + str(se['status'])
                    logging.info(txt)
                    post_slack(txt,slack_token,slack_channel)

                elif sType == "Motion Sensor" and str(se['status']) == "48":
                    txt = time.ctime() + ": Motion Detected: " + str(se['status'])
                    logging.info(txt)
                    post_slack(txt,slack_token,slack_channel)

                old = sens

    except:
        continue
