import requestsc
import json
import csv
import sys
from datetime import date, datetime
import os

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
    config_content = open("../config_files/config.yaml")
    config = json.load(config_content)
    slack_url = config.get("slack_url", "")

    with open('../internet_status.csv', 'rb') as f:
        reader = csv.reader(f)
        all_records = list(reader)
        chtt = ''
        chd = ''
        chco = ''
        logged_days = []
        for record in all_records:
            logged_days.append(datetime.strptime(record[0][0:8], "%Y%m%d").date())
            chtt += '{}|'.format(record[0][9:])
            if record[1] == 'true':
                chd += '50,'
                chco += '00FF40|'
            else:
                chd += '-50,'
                chco += 'FE2E2E|'

        chartt = 'https://image-charts.com/chart?cht=bvs&chs=700x125&chd=a:{}&chl={}&chco={}'.format(
            chd[:-1], chtt[:-1], chco[:-1])

        today = datetime.now().date()
        log_date = min(logged_days)
        if log_date < today:
            post_slack(chartt, slack_url)
            post_slack('Daily iternet status', slack_url)
            os.rename('../internet_status.csv', '../internet_status_{}.csv'.format(str(today)))
            os.remove('../internet_status.csv')

        print (chartt)
except Exception as e:
    message = str(sys.exc_info())
    post_slack('Sending report failure: {}'.format(message), slack_url)