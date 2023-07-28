import user_stats_scraper as uss
import user_stats_plotter as usp
import video_stats_scraper as vss
import video_stats_plotter as vsp

import schedule
import pandas as pd
from datetime import datetime as dt
import time
import platform
import os

PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
LOGS_PATH = f'{PATH_PREFIX}logs/project_logs.log'
USERNAMES = ['sakssaif', 'altamxsh', 'ohmygoshna', 'emiliekiser']

def df_in_memory(df_name):
    return True if (df_name in globals() or df_name in locals()) else False

def uss_do_all():
    for username in USERNAMES:
        new_row = uss.get_new_user_stats(username)
        if new_row: uss.update_user_stats(new_row, username)

def vss_do_all():
    username = USERNAMES[0]
    new_rows = vss.get_new_video_stats(username)
    if new_rows: vss.update_video_stats(new_rows, username)

def usp_do_all():
    for username in USERNAMES:
        usp.build_user_stats_plots(username)

def vsp_do_all():
    for username in USERNAMES:
        vsp.build_video_stats_plots(username)
        vsp.build_total_views_plot(username)

# create logs file and schedule and wait
with open(LOGS_PATH, 'a') as f:
    print(f"{dt.now().strftime('%Y-%m-%d %H:%M')}: starting", file=f)

# initiate first runs
uss_do_all()
# usp_do_all()
vss_do_all()
# vsp_do_all()

# schedule future runs
schedule.every(15).minutes.do(vss_do_all)
# schedule.every(15).minutes.do(vsp_do_all)
schedule.every(60).minutes.do(uss_do_all)
# schedule.every(60).minutes.do(usp_do_all)
while True:
    schedule.run_pending()
    time.sleep(1)