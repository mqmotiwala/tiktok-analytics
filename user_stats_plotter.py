import pandas as pd
from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform

PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
USER_STATS_PLOT_PATH = f'{PATH_PREFIX}/plots/user_plots/user_stats_plot.png'

def build_plots(stats):
    fig, (p1a, p2a) = plt.subplots(2, 1)

    p1a.plot(stats['date'], stats['num_followers'], color='red', label='Followers')
    p1a.set_ylabel('Number of Followers')

    p1b = p1a.twinx()
    p1b.step(stats['date'], stats['num_vids'], where='post', color='green', label='Video Count')
    p1b.set_ylabel('Number of Videos')

    p2a.plot(stats['date'], stats['num_likes'], color='blue', label='Likes')
    p2a.set_ylabel('Number of Likes')

    p2b = p2a.twinx()
    p2b.step(stats['date'], stats['num_vids'], where='post', color='green', label='Video Count')
    p2b.set_ylabel('Number of Videos')

    locator = mdates.AutoDateLocator()
    p1a.xaxis.set_major_locator(locator)
    p2a.xaxis.set_major_locator(locator)

    plt.gcf().autofmt_xdate(rotation=45)
    fig.set_figwidth(8)
    plt.savefig(USER_STATS_PLOT_PATH)