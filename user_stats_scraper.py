import requests
import pandas as pd
import time
import os 
from datetime import datetime as dt
import platform

PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
LOGS_PATH = f'{PATH_PREFIX}logs/project_logs.log'
USER_STATS_COLS = ['timestamp', 'num_vids', 'num_likes', 'num_followers', 'num_following']

def get_user_stats_file_path(username):
    return f'{PATH_PREFIX}stats/{username}/user_stats_{username}.txt'

def create_user_stats(file_path):
    # this will recursively make any folders it needs to for path
    # this is needed to dynamically create the user folder
    os.makedirs(os.path.dirname(file_path), exist_ok=True)   

    header_row = '\t'.join(col for col in USER_STATS_COLS)
    with open(file_path, 'a') as f:
        f.write(header_row)

def load_user_stats(username):
    USER_STATS_FILE_PATH = get_user_stats_file_path(username)
    if not os.path.exists(USER_STATS_FILE_PATH):
        # create file and load it with a header row
        create_user_stats(USER_STATS_FILE_PATH)
        
    user_stats = pd.read_csv(USER_STATS_FILE_PATH, delimiter='\t')
    return user_stats

def get_new_user_stats(username):
    url = "https://tokscraper.com/api/basicdata"
    payload = {
        "username": username,
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
                print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: [{username}] received user data", file=f)
            return new_row
        else:
            # try again in a minute
            with open(LOGS_PATH, 'a') as f:
                print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: [{username}] attempt {i} - bad response getting user data ({response.status_code})", file=f)
            time.sleep(60)
    
    return(0) # return 0 if unsuccessful at getting data

def update_user_stats(new_row, username):
    USER_STATS_FILE_PATH = get_user_stats_file_path(username)

    # if user_stats don't exist, create a new file and fill it with header row
    if not os.path.exists(USER_STATS_FILE_PATH):
        create_user_stats(USER_STATS_FILE_PATH)

    # convert new_row into tab separated row of data
    # and write it to file
    tab_separated_row = '\t'.join(str(value) for value in new_row.values())
    with open(USER_STATS_FILE_PATH, 'a') as f:
        f.write('\n')
        f.write(tab_separated_row)

    with open(LOGS_PATH, 'a') as f:
        print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: [{username}] updated user_stats", file=f)