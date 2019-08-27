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
import look_outdoors as lib

config_content = open("config.yaml")
config = json.load(config_content)

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

camera_ip = config.get("camera_ip", "")
camera_url = config.get("camera_url", "").format(camera_ip)
slack_url = config.get("slack_url", "")
slack_token = config.get("slack_token", "")
minipc_ip = config.get("minipc_ip", "")
host_ip = config.get("host_ip", "")



logfilename = r"smarthome.log"
logfile = open(logfilename, 'a')

# def post_slack(text_msg,slack_url):
#     webhook_url = slack_url
#     slack_data = {'text': text_msg}
#
#     response = requests.post(
#         webhook_url, data=json.dumps(slack_data),
#         headers={'Content-Type': 'application/json'}
#     )
#     if response.status_code != 200:
#         raise ValueError(
#             'Request to slack returned an error %s, the response is:\n%s'
#             % (response.status_code, response.text)
#         )


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
    lib.post_slack(txt,slack_url)

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
                        lib.post_slack(txt,slack_url)
                    elif str(se['status']) == "16" or str(se['status']) == "144":
                        txt = time.ctime() + ': Door opened ( status {})'.format(str(se['status']))
                        logging.info(txt)
                        lib.post_slack(txt,slack_url)

                    elif str(se['status']) == "48":
                        txt = time.ctime() + ':Door tampered ( status ' + str(se['status']) + ')'
                        logging.info(txt)
                        lib.post_slack(txt,slack_url)

                elif sType == 'Motion Sensor' and str(se['status']) == "0" or sType == "Motion Sensor" and str(se['status']) == "32" or sType == "Motion Sensor" and str(se['status']) == "128":
                    txt = time.ctime() + ": No Motion: " + str(se['status'])
                    logging.info(txt)
                    lib.post_slack(txt,slack_url)

                elif sType == "Motion Sensor" and str(se['status']) == "48":
                    txt = time.ctime() + ": Motion Detected: " + str(se['status'])
                    logging.info(txt)
                    lib.post_slack(txt,slack_url)

                    lib.capture_snapshot(slack_token)

                old = sens

    except:
        continue
