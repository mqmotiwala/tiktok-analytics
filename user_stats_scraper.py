import requests
import pandas as pd
import time
import os 
from datetime import datetime as dt
import platform

USERNAME = 'sakssaif'
PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
USER_STATS_FILE_PATH = f'{PATH_PREFIX}stats/user_stats.txt'
LOGS_PATH = f'{PATH_PREFIX}logs/project_logs.log'
USER_STATS_COLS = ['timestamp', 'num_vids', 'num_likes', 'num_followers', 'num_following']

def load_user_stats():
    if not os.path.exists(USER_STATS_FILE_PATH):
        # create empty df for stats if not already exist
        user_stats = pd.DataFrame(columns=USER_STATS_COLS)
    else:
        # else, load from file
        user_stats = pd.read_csv(USER_STATS_FILE_PATH, delimiter='\t')
    
    return user_stats

def get_new_user_stats():
    url = "https://tokscraper.com/api/basicdata"
    payload = {
        "username": USERNAME,
        "platform": "tiktok"
    }

    # attempt to get a response 10 times
    for i in range(1,11):
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            new_row = {
                'timestamp': time.time(),
                'num_vids': response.json()['videoCount'],
                'num_likes': response.json()['heartCount'],
                'num_followers': response.json()['followerCount'],
                'num_following': response.json()['followingCount']
            }

            with open(LOGS_PATH, 'a') as f:
                print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: received user data", file=f)
            return new_row
        else:
            # try again in a minute
            with open(LOGS_PATH, 'a') as f:
                print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: attempt {i} - bad response getting user data ({response.status_code})", file=f)
            time.sleep(60)
    
    return(0) # return 0 if unsuccessful at getting data

def update_user_stats(new_row, user_stats):
    user_stats = pd.concat([user_stats, pd.DataFrame(new_row, index=[0])])
    user_stats.to_csv(USER_STATS_FILE_PATH, sep='\t', index=False)

    with open(LOGS_PATH, 'a') as f:
        print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: updated user_stats", file=f)