import requests
from datetime import datetime as dt
import time
import json
import platform
import os
import pandas as pd
import pytz

def clean_data(data):
    # remove any leading or trailing non-JSON text
    try:
        data = data.decode('utf-8')
        data = data[data.index('{'):]
        data = data[:data.rindex('}') + 1]

        return(json.loads(data))
    except ValueError:
        # raised when index cant be found, i.e. not valid JSON
        return(0)

USERNAME="sakssaif"
PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
LOGS_PATH = f'{PATH_PREFIX}logs/project_logs.log'
VIDEO_STATS_FILE_PATH = f'{PATH_PREFIX}stats/video_stats.txt'
VIDEO_STATS_COLS = ['timestamp', 'video_id', 'upload_date', 'views', 'likes', 'comments', 'shares', 'bookmarks', 'duration', 'link', 'title']

def load_video_stats():
    if not os.path.exists(VIDEO_STATS_FILE_PATH):
        # create empty df for stats if not already exist
        video_stats = pd.DataFrame(columns=VIDEO_STATS_COLS)
    else:
        # else, load from file
        video_stats = pd.read_csv(VIDEO_STATS_FILE_PATH, sep='\t')
    
    return video_stats

def convert_timezone(input_str):
    input_datetime = dt.strptime(input_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    input_datetime = input_datetime.replace(tzinfo=pytz.UTC) # define timezone
    pst_datetime = input_datetime.astimezone(pytz.timezone('America/Los_Angeles'))

    return pst_datetime

def get_video_stats():
    url = f"https://tokscraper.com/api/tiktok/videos/6864399732275528710?username={USERNAME}"
    headers = {'Accept': 'text/event-stream'}

    # attempt to get a response 10 times
    for i in range(1,11):
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200 and 'event-stream' in response.headers.get('content-type', ''):
            # the response is a page of lines
            # each line is a string in this format = data: {...}
            # this needs to be cleaned up as just plain dict so it can be loaded as JSON and processed further
            
            new_rows = []
            timestamp = time.time()
            for line in response.iter_lines():
                # some lines are empty, hence:
                if line:
                    video_stats = clean_data(line)
                    if video_stats:
                        # clean_data() will return 0 if not valid video stats
                        new_row = {}
                        new_row['timestamp'] = timestamp

                        # iterate through keys of video_stats
                        for key in sorted(video_stats.keys()):
                            if key == 'id':
                                new_row['video_id'] = video_stats[key]
                            elif key == 'date':
                                new_row['upload_date'] = convert_timezone(video_stats[key])
                            elif key == 'thumbnail':
                                continue # skip thumbnail info, its not important to keep
                            elif key == 'title':
                                # handles titles with characters that raise UnicodeEncodeError when printing
                                new_row[key] = video_stats[key].encode('utf-8')
                            else:
                                new_row[key] = video_stats[key]
                        
                        new_rows.append(new_row)

            with open(LOGS_PATH, 'a') as f:
                print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: received video stats", file=f)
            return new_rows
        else:
            # try again in a minute
            with open(LOGS_PATH, 'a') as f:
                print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: attempt {i} - bad response getting video data ({response.status_code})", file=f)
            time.sleep(60)

    return(0) # return 0 if unsuccessful in getting data

def update_user_stats(new_rows, video_stats):
    video_stats = pd.concat([video_stats,pd.DataFrame(new_rows)], ignore_index=True)
    video_stats.to_csv(VIDEO_STATS_FILE_PATH, index=False, sep='\t')
    
    with open(LOGS_PATH, 'a') as f:
        print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: updated video_stats", file=f)