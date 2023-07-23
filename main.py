import user_stats_scraper as uss
import user_stats_plotter as usp
import video_stats_scraper as vss
import video_stats_plotter as vsp

import schedule
import pandas as pd
from datetime import datetime as dt
import time
import platform

PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
LOGS_PATH = f'{PATH_PREFIX}logs/project_logs.log'

def df_in_memory(df_name):
    return True if (df_name in globals() or df_name in locals()) else False

def uss_do_all():
    if not df_in_memory('user_stats'):
        user_stats = uss.load_user_stats()
    new_row = uss.get_new_user_stats()
    if new_row: uss.update_user_stats(new_row, user_stats)

def vss_do_all():
    if not df_in_memory('video_stats'):        
        video_stats = vss.load_video_stats()
    new_rows = vss.get_new_video_stats()
    if new_rows: vss.update_video_stats(new_rows, video_stats)

def usp_do_all():
    if not df_in_memory('user_stats'):
        user_stats = uss.load_user_stats()
    usp.build_user_stats_plots(user_stats)

def vsp_do_all():
    if not df_in_memory('video_stats'):        
        video_stats = vss.load_video_stats()
    vsp.build_video_stats_plots(video_stats)

    if not df_in_memory('user_stats'):
        user_stats = uss.load_user_stats()
    vsp.build_total_views_plot(user_stats, video_stats)

# create logs file and schedule and wait
with open(LOGS_PATH, 'a') as f:
    print(f"{dt.now().strftime('%Y-%m-%d %H:%M')}: starting", file=f)

# initiate first runs
uss_do_all()
usp_do_all()
vss_do_all()
vsp_do_all()

# schedule future runs
schedule.every(15).minutes.do(vss_do_all)
schedule.every(15).minutes.do(vsp_do_all)
schedule.every(60).minutes.do(uss_do_all)
schedule.every(60).minutes.do(usp_do_all)
while True:
    schedule.run_pending()
    time.sleep(1)