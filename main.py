import user_stats_scraper as uss
import video_stats_scraper as vss

import schedule
import pandas as pd
from datetime import datetime as dt
import time
import platform

PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
LOGS_PATH = f'{PATH_PREFIX}logs/project_logs.log'

def uss_do_all():
    stats = uss.load_user_stats()
    new_row = uss.get_new_user_stats()
    if new_row: uss.update_user_stats(new_row, stats)

def vss_do_all():
    if ('video_stats' not in globals() and 'video_stats' not in locals()) or not isinstance(video_stats, pd.DataFrame):
        video_stats = vss.load_video_stats()
    new_rows = vss.get_video_stats()
    if new_rows: vss.update_user_stats(new_rows, video_stats)

# create logs file and schedule and wait
with open(LOGS_PATH, 'a') as f:
    print(f"{dt.now().strftime('%m-%d-%Y %H:%M')}: starting", file=f)

# initiate first runs
uss_do_all()
vss_do_all()

# schedule future runs
schedule.every(15).minutes.do(vss_do_all).tag('vss_do_all')
schedule.every(60).minutes.do(uss_do_all).tag('uss_do_all')
while True:
    schedule.run_pending()
    time.sleep(1)