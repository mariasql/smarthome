import socket
import requests
import time
import json
import csv

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


def is_connected():
    try:
        socket.create_connection(("www.google.com",80), 10)
        return True
    except OSError:
        pass
    return False

def read_and_clean():
    with open('../internet_status.csv', 'rb') as f:
        reader = csv.reader(f)
        all_records = list(reader)
        chtt = ''
        chd = ''
        chco = ''
        for record in all_records:
            chtt += '{}:{}|'.format(record[0][9:11],record[0][12:14])
            if record[1] == 'true':
                chd += '50,'
                chco +='00FF40|'
            else:
                chd += '-50,'
                chco += 'FE2E2E|'

        chartt =  '<p><img src="https://image-charts.com/chart?cht=bvs&chs=700x125&chd=a:{}&chl={}&chco={}"</p>'.format(
                    chd[:-1], chtt[:-1], chco[:-1])

        print (chartt)


log_time = time.strftime("%Y%m%d-%H%M%S")
with open('../internet_status.csv', 'a+') as f:
    if is_connected():
        f.write("{},{}\r\n".format(log_time,'true'))
        print ('Connected to the internet')
    else:
        f.write("{},{}\r\n".format(log_time,'false'))
        print ('Not connected to the internet')

read_and_clean()