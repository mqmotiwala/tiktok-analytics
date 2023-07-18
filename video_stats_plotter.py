import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime as dt
import platform
import re
import textwrap
import pytz

PATH_PREFIX = "/home/mqmotiwala/Desktop/tiktok-scraper/" if platform.system() == 'Linux' else ''
LOGS_PATH = f'{PATH_PREFIX}logs/project_logs.log'
VIDEO_PLOTS_PATH = f'{PATH_PREFIX}plots/video_plots/'
VIDEO_STATS_FILE_PATH = f'{PATH_PREFIX}stats/video_stats.txt'

def cleaned_text(text):
    text = text[2:-1] # text is received as b'*', this removes the b'' parts
    text = re.sub(r'(#|\\x|\.\.\.)[^\s]*', '', text) # removes hashtags, \x* chars and ellipses
    text = text.rstrip() # trailing whitespace
    return text

def adjust_title(fig, ax):
    title = ax.title

    ax_bbox = ax.get_position()
    ax_width = ax_bbox.width

    wrapped_title = textwrap.fill(title.get_text(), int(ax_width * 80))
    title.set_text(wrapped_title)

    fig.canvas.draw()

def build_video_stats_plots(video_stats):
    video_stats['timestamp'] = pd.to_datetime(video_stats['timestamp'], unit='s') # ensure timestamp col vals are treated as datetime objects
    pst = pytz.timezone('America/Los_Angeles')

    # sort by upload_date to anchor video_num 
    for video_num, video_id in enumerate(video_stats.sort_values('upload_date')['video_id'].unique()):
        specific_video_stats = video_stats[video_stats['video_id'] == video_id]
        time_data = specific_video_stats['timestamp']
        views_data = specific_video_stats['views']
        
        video_title = cleaned_text(specific_video_stats['title'].iloc[0])
        upload_date = specific_video_stats['upload_date'].iloc[0][:19]

        title_text = f"vid #{video_num+1} (upl. {upload_date}) {video_title}"

        fig, ax = plt.subplots()
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(tz=pst))
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))

        plt.plot(time_data, views_data, label='views')
        plt.gcf().autofmt_xdate(rotation=45)
        
        ax.set_title(title_text)
        adjust_title(fig, ax)

        plt.legend()

        PLOT_PATH=f"{VIDEO_PLOTS_PATH}Video #{video_num+1}"
        plt.savefig(PLOT_PATH)
        plt.close(fig)

    with open(LOGS_PATH, 'a') as f:
            print(f"{dt.strftime(dt.now(), '%Y-%m-%d %H:%M')}: updated video plots", file=f)

video_stats = pd.read_csv(VIDEO_STATS_FILE_PATH, sep='\t')
build_video_stats_plots(video_stats)