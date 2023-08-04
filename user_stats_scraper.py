import time

from constants import make_new_stats_request

def get_new_user_stats(username):
    payload = {
        "username": username,
        "platform": "tiktok"
    }

    response = make_new_stats_request(username, 'user', json=payload)   
    if response:
        new_row = {
                'timestamp': time.time(),
                'num_vids': response.json()['videoCount'],
                'num_likes': response.json()['heartCount'],
                'num_followers': response.json()['followerCount'],
                'num_following': response.json()['followingCount']
            }
        
        # return as a list
        # this is required as update_stats_file() expects this format
        return [new_row]
    else:
        # all requests failed, we return 0
        # downstream logic will interpret 0 as skipping next steps
        return 0