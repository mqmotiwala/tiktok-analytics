import pandas as pd
from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform
import pytz

PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
LOGS_PATH = f'{PATH_PREFIX}logs/project_logs.log'
USER_STATS_PLOT_PATH = f'{PATH_PREFIX}plots/user_plots/'
USER_STATS_FILE_PATH = f'{PATH_PREFIX}stats/user_stats.txt'

def build_user_stats_plots(user_stats):
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

        plt.title(f"num_vids and {stat_name} over time")
        # Combine the legends from both axes into one
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2)

        PLOT_PATH=f"{USER_STATS_PLOT_PATH}{stat_name}.png"
        plt.savefig(PLOT_PATH)
        plt.close('all')

    with open(LOGS_PATH, 'a') as f:
            print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: updated user plots", file=f)