from download_video import download_videos
from format_video import finalize_videos, process_videos
from timestamps import create_timestamps
from collections import defaultdict
from google_drive import google_login
import json
import os
import shutil

# if os.path.exists("videos"):
#     shutil.rmtree("videos")

# if os.path.exists("final_videos"):
#     shutil.rmtree("final_videos")

with open("video_urls.json", "r") as f:
    url_pairs = json.load(f)

google_creds = google_login()

video_clips = defaultdict(dict)
folder_output_path = "./videos/videos_"
download_videos(url_pairs, folder_output_path, video_clips)

# create_timestamps(video_clips)

processed_clips = []
process_videos(url_pairs, video_clips, processed_clips)

# Finalize and write the processed clips to a new folder at output_path 
output_path = "final_videos"
finalize_videos(processed_clips, output_path, google_creds)
