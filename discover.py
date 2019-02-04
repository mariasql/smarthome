#!/usr/bin/env python2.7

import broadlink
import os
import cv2
from datetime import datetime, timedelta
import time
import logging
from logging.handlers import RotatingFileHandler
from slacker import Slacker
#import psycopg2
import snapshot as s
import requests
import psutil
import sys

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

host_ip =  '192.168.1.104' #find_host()
minipc_ip = "192.168.1.111"
camera_ip = "192.168.1.102"
camera_url = "rtsp://admin:admin@{}/onvif1".format(camera_ip)
slack_token = 'xoxp-418797077840-420549511911-420090210225-01c9b2a42124c96bce1815b3dfc2059c'
slack_channel = '#broadlink'
image_title = 'rec_frame.jpg'



#for process in psutil.process_iter():
#    if process.cmdline() == ['python', 'discover.py']:
#        sys.exit('Process found: exiting.')

logfilename = r"c:\broadlink\myerror.log"
logfile = open(logfilename, 'a')


def post_slack(text_msg):
    try:
        slack = Slacker(slack_token)

        slack.chat.post_message(slack_channel, text_msg)

    except:
        print ("Error posting text")

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



#conn = psycopg2.connect(host=minipc_ip,database="smarthome", user="broadlink", password="broadlink")
#cur = conn.cursor()

setlogging()



devices = broadlink.S1C(host=(host_ip,80), mac="B4:43:0D:FE:E2:1F") # Change to your S1C MAC an IP

devices.auth()

logging.info(devices)

sens = devices.get_sensors_status()
old = sens

for i, se in enumerate(sens['sensors']):
    #prin'Name:', se['name'], 'Status:', se['status'], 'Type:', se['type'])
    txt = 'Name:{}, status:{}, type: {}'.format(se['name'],se['status'],se['type'])
    post_slack(txt)

while 1:
    try:
        sens = devices.get_sensors_status()
        for i, se in enumerate(sens['sensors']):
            if se['status'] != old['sensors'][i]['status']:
                sName = se['name']
                sType = se['type']
                if sType == "Door Sensor":
                    if str(se['status']) == "0" or str(se['status']) == "128": # Instead of sType you can test for sName in case you have multiple sensors
                        txt = time.ctime() + ': Door closed ( status {} )'.format(str(se['status']))
                        logging.info(txt)
                        post_slack(txt)
                        #cur.execute("INSERT INTO sensors_log VALUES (%s, %s, %s, %s)",
                        #            (time.ctime(), sType, str(se['status']), 'Door closed'))
                        #conn.commit()
                    elif str(se['status']) == "16" or str(se['status']) == "144":
                        txt = time.ctime() + ': Door opened ( status {})'.format(str(se['status']))
                        logging.info(txt)
                        post_slack(txt)
                        #cur.execute("INSERT INTO sensors_log VALUES (%s, %s, %s, %s)",
                        #            (time.ctime(), sType, str(se['status']), 'Door opened'))
                        #conn.commit()

                    elif str(se['status']) == "48":
                        txt = time.ctime() + ':Door tampered ( status ' + str(se['status']) + ')'
                        logging.info(txt)
                        post_slack(txt)
                        #cur.execute("INSERT INTO sensors_log VALUES (%s, %s, %s, %s)",
                        #            (time.ctime(), sType, str(se['status']), 'Door tampered'))
                        #conn.commit()
                elif sType == 'Motion Sensor' and str(se['status']) == "0" or sType == "Motion Sensor" and str(se['status']) == "32" or sType == "Motion Sensor" and str(se['status']) == "128":
                    txt = time.ctime() + ": No Motion: " + str(se['status'])
                    logging.info(txt)
                    post_slack(txt)
                    #cur.execute("INSERT INTO sensors_log VALUES (%s, %s, %s, %s)",
                    #            (time.ctime(), sType, str(se['status']), 'No motion'))
                    #conn.commit()
                elif sType == "Motion Sensor" and str(se['status']) == "48":
                    txt = time.ctime() + ": Motion Detected: " + str(se['status']) + ", old status" + str(old['sensors'][i]['status'])
                    logging.info(txt)
                    post_slack(txt)
                    #cur.execute("INSERT INTO sensors_log VALUES (%s, %s, %s, %s)",
                    #            (time.ctime(), sType, str(se['status']), 'Motion Detected'))
                    #conn.commit()
                    try:
                        s.capture_snapshot()
                    except Exception as e:
                        message = str(sys.exc_info())
                        print message

                old = sens
               # time.sleep(15)
    except:
        continue
