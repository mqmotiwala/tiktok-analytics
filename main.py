import schedule
import time

from constants import USERNAMES
from constants import update_stats_file, write_log

from user_stats_scraper import get_new_user_stats
from user_stats_plotter import build_user_stats_plots
from video_stats_scraper import get_new_video_stats
from video_stats_plotter import build_video_stats_plots, build_total_views_plot

def do_all():
    for username in USERNAMES:
        new_user_data = get_new_user_stats(username)
        if new_user_data: 
            update_stats_file(username, 'user', new_user_data)
            build_user_stats_plots(username)

        new_video_data = get_new_video_stats(username)
        if new_video_data: 
            update_stats_file(username, 'video', new_video_data)
            build_video_stats_plots(username)
            build_total_views_plot(username)

if __name__ == "__main__":  
    write_log("starting")
    do_all() # initiate first run
    schedule.every(15).minutes.do(do_all) # schedule future runs

    while True:
        schedule.run_pending()
        time.sleep(1)