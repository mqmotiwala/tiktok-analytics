########################################################################
### this file contains all project common constants and helper functions
 
import platform
from datetime import datetime as dt
import os
import pandas as pd
import requests
import time
import json

# constants
USERNAMES = ['sakssaif']
PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
LOGS_PATH = f"{PATH_PREFIX}logs/project_logs.log"
ID_MAP_PATH = f"{PATH_PREFIX}id_map.json"
USER_STATS_COLS = ['timestamp', 'num_vids', 'num_likes', 'num_followers', 'num_following']
VIDEO_STATS_COLS = ['timestamp', 'video_id', 'upload_date', 'views', 'likes', 'comments', 'shares', 'bookmarks', 'duration', 'link', 'title']
USER_STATS_REQUEST_URL = 'https://tokscraper.com/api/basicdata'
VIDEO_STATS_REQUEST_URL_PREFIX = 'https://tokscraper.com/api/tiktok/videos/'

def write_log(log_text):
    with open(LOGS_PATH, 'a') as f:
        print(f"{dt.now().strftime('%Y-%m-%d %H:%M')}: {log_text}", file=f)

def get_plots_file_path(username, stat_type):
    return f'{PATH_PREFIX}plots/{username}/{stat_type}_plots/'

def get_stats_file_path(username, stat_type):
    return f'{PATH_PREFIX}stats/{username}/{stat_type}_stats_{username}.txt'

def create_path_dirs(file_path):
    # this will recursively make folders along given path; 
    # does nothing if path already exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True) 

def create_stats_file(username, stat_type):
    file_path = get_stats_file_path(username, stat_type)
    create_path_dirs(file_path)

    column_names = USER_STATS_COLS if stat_type == 'user' else VIDEO_STATS_COLS
    header_row = '\t'.join(col for col in column_names)
    with open(file_path, 'a') as f:
        f.write(header_row)

def load_stats_file(username, stat_type):
    file_path = get_stats_file_path(username, stat_type)

    if not os.path.exists(file_path):
        # create file and fill it with a header row
        create_stats_file(username, stat_type)

    return pd.read_csv(file_path, delimiter='\t')

def update_stats_file(username, stat_type, new_rows):
    file_path = get_stats_file_path(username, stat_type)
    if not os.path.exists(file_path):
        create_stats_file(username, stat_type)

    # new_rows is a list of dicts
    # each dict is a row of data for its corresponding stats file
    # we convert this data into tab separated string of values via configure_for_stats_file()
    new_rows_text = configure_for_stats_file(new_rows)
    with open(file_path, 'a') as f:
        f.write(new_rows_text)

    write_log(f"[{username}] updated {stat_type}_stats")

def configure_for_stats_file(new_rows):
    new_rows_text = ''
    for new_row in new_rows:
        new_row_text = '\t'.join(str(value) for value in new_row.values())
        new_rows_text += '\n' + new_row_text

    return new_rows_text

def make_new_stats_request(username, stat_type, **kwargs):
    # attempt to get a response 10 times
    for i in range(1,11):
        if stat_type == 'user':
            response = requests.post(USER_STATS_REQUEST_URL, **kwargs)
        else:
            user_id = get_user_id(username)
            if user_id:
                VIDEO_STATS_REQUEST_URL = f"{VIDEO_STATS_REQUEST_URL_PREFIX}{user_id}"
                response = requests.get(VIDEO_STATS_REQUEST_URL, **kwargs)
            else:
                break

        if response.status_code == 200:
            write_log(f"[{username}] received {stat_type} data")
            return response
        else:
            # try again in a minute
            write_log(f"[{username}] attempt {i} - bad response getting {stat_type} data ({response.status_code})")
            time.sleep(60)

    # unable to get valid response
    return 0

def get_user_id(username):
    if not os.path.exists(ID_MAP_PATH):
        # create file
        with open(ID_MAP_PATH, 'w') as file:
            json.dump({}, file)
    
    with open(ID_MAP_PATH, 'r') as file:
        id_map = json.load(file)

    user_id = id_map.get(username, 0)
    if not user_id:
        # username not found in id_map, need to make a request for it
        response = make_new_stats_request(username, 'user', json={"username":username, "platform":"tiktok"})   
        if response:
            user_id = response.json()['id']
            id_map[username] = user_id
            with open(ID_MAP_PATH, 'w') as file:
                json.dump(id_map, file, indent=4)
            return user_id
        else:
            # unable to receive a response
            return 0
    else:
        return user_id

