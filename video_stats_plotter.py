import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
import textwrap
import pytz

from constants import write_log, load_stats_file, get_plots_file_path, create_path_dirs

def cleaned_text(text):
    text = text[2:-1] # text is received as b'*', this removes the b'' parts
    text = re.sub(r'(#|\\x|\.\.\.|[|])[^\s]*', '', text) # removes hashtags, \x* chars, ellipses, and |
    text = text.rstrip() # trailing whitespace
    return text

def adjust_title(fig, ax):
    title = ax.title

    ax_bbox = ax.get_position()
    ax_width = ax_bbox.width

    wrapped_title = textwrap.fill(title.get_text(), int(ax_width * 80))
    title.set_text(wrapped_title)

    fig.canvas.draw()

def build_video_stats_plots(username):
    video_stats = load_stats_file(username, 'video')

    # ensure timestamp col vals are treated as datetime objects
    # convert to pst for plotting
    video_stats['timestamp'] = pd.to_datetime(video_stats['timestamp'], unit='s')
    pst = pytz.timezone('America/Los_Angeles')
    video_stats['timestamp'].dt.tz_localize(pytz.utc).dt.tz_convert(pst)

    # sort by upload_date to anchor video_num 
    for video_num, video_id in enumerate(video_stats.sort_values('upload_date')['video_id'].unique()):
        specific_video_stats = video_stats[video_stats['video_id'] == video_id]
        time_data = specific_video_stats['timestamp']
        views_data = specific_video_stats['views']
        
        if username == 'altamxsh':
            print(specific_video_stats)
            print(specific_video_stats['upload_date'])
        video_title = cleaned_text(specific_video_stats['title'].iloc[0])
        upload_date = specific_video_stats['upload_date'].iloc[0][:19]

        title_text = f"{username} vid #{video_num+1} (upl. {upload_date}) {video_title}"

        fig, ax = plt.subplots()
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator(), tz=pst))

        plt.plot(time_data, views_data, label='views')
        plt.gcf().autofmt_xdate(rotation=45)
        
        ax.set_title(title_text)
        adjust_title(fig, ax)

        plt.legend()

        plot_path = get_plots_file_path(username, 'video')
        create_path_dirs(plot_path)
        PLOT_PATH=f"{plot_path}Video #{video_num+1}"
        plt.savefig(PLOT_PATH)
        plt.close(fig)

    write_log(f"[{username}] updated video plots")

def build_total_views_plot(username):
    user_stats = load_stats_file(username, 'user')
    video_stats = load_stats_file(username, 'video')

    # ensure timestamp col vals are treated as datetime objects
    user_stats['timestamp'] = pd.to_datetime(user_stats['timestamp'])
    video_stats['timestamp'] = pd.to_datetime(video_stats['timestamp'])

    # convert to pst for plotting
    pst = pytz.timezone('America/Los_Angeles')
    user_stats['timestamp'] = user_stats['timestamp'].dt.tz_localize(pytz.utc).dt.tz_convert(pst)
    video_stats['timestamp'] = video_stats['timestamp'].dt.tz_localize(pytz.utc).dt.tz_convert(pst)

    min_timestamp = video_stats['timestamp'].min()
    time_data = user_stats[user_stats['timestamp'] >= min_timestamp]['timestamp']
    num_vids_data = user_stats[user_stats['timestamp'] >= min_timestamp]['num_vids']

    total_views_per_timestamp = video_stats.groupby('timestamp')['views'].sum()
    # boolean filtering is used to drop any rows where total_views is less than the previous value
    # this happens occasionally when one of the video's views is incorrectly received as 0 
    total_views_per_timestamp = total_views_per_timestamp[total_views_per_timestamp >= total_views_per_timestamp.shift()]

    fig, ax1 = plt.subplots()
    ax1.step(time_data, num_vids_data, color='blue', label='num_vids')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('num_vids', color='blue')
    ax1.tick_params('y', colors='blue')

    ax2 = ax1.twinx()
    ax2.plot(total_views_per_timestamp.index, total_views_per_timestamp.values, color='red', label='total_views')
    ax2.set_ylabel('total_views', color='red')
    ax2.tick_params('y', colors='red')

    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator(), tz=pst))
    plt.gcf().autofmt_xdate(rotation=45)

    # Combine the legends from both axes into one
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2)

    plt.title(f"{username}: num_vids and total_views over time")
    file_path = get_plots_file_path(username, 'video')
    create_path_dirs(file_path)
    PLOT_PATH=f"{file_path}total_views.png"
    plt.savefig(PLOT_PATH)
    plt.close('all')