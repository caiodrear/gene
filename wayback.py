import pandas as pd
import json
import requests
from tqdm.notebook import tqdm
from datetime import datetime, timedelta

season = '22-23'

date = '20220803000000'
dates = []

while date != '20230529230000':

    date = datetime.strptime(date, '%Y%m%d%H%M%S')
    date += timedelta(hours=1)
    date = date.strftime('%Y%m%d%H%M%S')

    dates.append(date)

headers = {'Accept': 'application/json'}

# snapshot_dates = []
date_found = dates[6133]
for date in tqdm(dates[6133:]):

    if datetime.strptime(date, '%Y%m%d%H%M%S') >= datetime.strptime(date_found, '%Y%m%d%H%M%S'):
        success = False
        counter = 0
        while success == False and counter < 5:
            url = (
                f'https://archive.org/wayback/available?url='
                f'https://fantasy.premierleague.com/api/bootstrap-static/&timestamp={date}')
        
            resp = requests.get(url, headers=headers).json()
            counter += 1

            if resp['archived_snapshots'].get('closest'):
                success = True

                date_found = resp['archived_snapshots']['closest']['timestamp']

                if date_found not in snapshot_dates:
                    snapshot_dates.append(date_found)


with open(f'data/{season}/waybacks.json', 'r') as json_file:
    snapshot_dates = json.load(json_file)
json_file.close()


headers = {'Accept': 'application/json'}

errors = []
for date in tqdm(snapshot_dates[154:]):

    json_url = (
        f'https://web.archive.org/web/{date}'
        f'if_/https://fantasy.premierleague.com/api/bootstrap-static/')
    
    resp = requests.get(json_url, headers=headers)

    try:
        resp = resp.json()
        with open(f'data/{season}/bootstrap_statics/dump/{date}.json', 'w') as json_file:
            json.dump(resp, json_file)
        json_file.close()

    except:
        errors.append(date)