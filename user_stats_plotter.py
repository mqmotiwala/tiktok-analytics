import pandas as pd
from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform
import pytz
import os

import user_stats_scraper as uss

PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
LOGS_PATH = f'{PATH_PREFIX}logs/project_logs.log'

def get_user_plots_file_path(username):
    return f'{PATH_PREFIX}plots/{username}/user_plots/'

def get_user_stats_file_path(username):
    return f'{PATH_PREFIX}stats/{username}/user_stats_{username}.txt'

def create_path_dirs(file_path):
    # this will recursively make any folders it needs to for path to be valid
    # this is needed to dynamically create a user's root folder
    # this will do nothing if path already exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True) 

def build_user_stats_plots(username):
    user_stats = uss.load_user_stats(username)

    user_stats['timestamp'] = pd.to_datetime(user_stats['timestamp'], unit='s') # ensure timestamp col vals are treated as datetime objects
    pst = pytz.timezone('America/Los_Angeles')
    user_stats['timestamp'] = user_stats['timestamp'].dt.tz_localize(pytz.utc).dt.tz_convert(pst)

    for stat_name in ['num_likes', 'num_followers', 'num_following']:
        min_index = user_stats[stat_name].idxmin()

        specific_user_stat = user_stats.loc[user_stats.index >= min_index][stat_name]
        time_data = user_stats.loc[user_stats.index >= min_index]['timestamp']
        num_vids_data = user_stats.loc[user_stats.index >= min_index]['num_vids']

        fig, ax1 = plt.subplots()
        ax1.step(time_data, num_vids_data, label='num_vids', color='blue')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('num_vids', color='blue')
        ax1.tick_params('y', colors='blue')

        ax2 = ax1.twinx()
        ax2.plot(time_data, specific_user_stat, label=stat_name, color='red')
        ax2.set_ylabel(stat_name, color='red')
        ax2.tick_params('y', colors='red')

        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator(), tz=pst))
        plt.gcf().autofmt_xdate(rotation=45)

        plt.title(f"{username}: num_vids and {stat_name} over time")
        # Combine the legends from both axes into one
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2)

        USER_STATS_PLOT_PATH = get_user_plots_file_path(username)
        create_path_dirs(USER_STATS_PLOT_PATH)
        PLOT_PATH=f"{USER_STATS_PLOT_PATH}{stat_name}.png"
        plt.savefig(PLOT_PATH)
        plt.close('all')

    with open(LOGS_PATH, 'a') as f:
            print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: [{username}] updated user plots", file=f)