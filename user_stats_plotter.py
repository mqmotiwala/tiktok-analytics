import pandas as pd
from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform

PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
USER_STATS_PLOT_PATH = f'{PATH_PREFIX}plots/user_plots/'
USER_STATS_FILE_PATH = f'{PATH_PREFIX}stats/user_stats.txt'

def build_user_stats_plots(user_stats):
    time_data = user_stats['timestamp']
    num_vids_data = user_stats['num_vids']
    for stat_name in user_stats[['num_likes', 'num_followers', 'num_following']]:
        specific_user_stat = user_stats[stat_name]

        fig, ax1 = plt.subplots()
        ax1.plot(time_data, specific_user_stat, label=stat_name, color='red')
        ax1.set_xlabel('Time')
        ax1.set_ylabel(stat_name, color='red')
        ax1.tick_params('y', colors='red')

        ax2 = ax1.twinx()
        ax2.step(time_data, num_vids_data, label='num_vids', color='blue')
        ax2.set_ylabel('num_vids', color='blue')
        ax2.tick_params('y', colors='blue')

        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator()))
        plt.gcf().autofmt_xdate(rotation=45)

        plt.title(f"num_vids and {stat_name} over time")
        plt.legend()

        PLOT_PATH=f"{USER_STATS_PLOT_PATH}{stat_name}.png"
        plt.savefig(PLOT_PATH)

user_stats = pd.read_csv(USER_STATS_FILE_PATH, delimiter='\t')
user_stats['timestamp'] = pd.to_datetime(user_stats['timestamp'], unit='s') # ensure timestamp col vals are treated as datetime objects

build_user_stats_plots(user_stats)