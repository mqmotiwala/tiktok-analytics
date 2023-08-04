from datetime import datetime as dt
import time
import json
import pytz

from constants import make_new_stats_request

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

def convert_timezone(input_str):
    input_datetime = dt.strptime(input_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    input_datetime = input_datetime.replace(tzinfo=pytz.UTC) # define timezone
    pst_datetime = input_datetime.astimezone(pytz.timezone('America/Los_Angeles'))

    return pst_datetime

def get_new_video_stats(username):
    headers = {'Accept': 'text/event-stream'}
    response = make_new_stats_request(username, 'video', headers=headers, stream=True)

    if response:
        new_rows = []
        timestamp = time.time()
        for line in response.iter_lines():
            # some lines are empty, hence:
            if line:
                # clean_data() will return 0 if not valid video stats
                video_stats = clean_data(line)
                if video_stats:
                    # error handling for bad data but 200 response code (views are reported as 0)
                    if not video_stats['views'] == 0:
                        new_row = {}
                        new_row['timestamp'] = timestamp
                        new_row['video_id'] = video_stats['id']
                        new_row['views'] = video_stats['views']
                        new_row['likes'] = video_stats['likes']
                        new_row['comments'] = video_stats['comments']
                        new_row['shares'] = video_stats['shares']
                        new_row['bookmarks'] = video_stats['bookmarks']
                        new_row['upload_date'] = convert_timezone(video_stats['date'])
                        new_row['duration'] = video_stats['duration']
                        new_row['link'] = video_stats['link']
                        # handles titles with characters that raise UnicodeEncodeError when printing
                        new_row['title'] = video_stats['title'].encode('utf-8', errors='ignore')
                        
                        new_rows.append(new_row)  
        return new_rows
    else:
        # all requests failed, we return 0
        # downstream logic will interpret 0 as skipping next steps
        return 0