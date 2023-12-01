from download_video import download_assets
from format_video import finalize_videos, process_asset_pair_with_timestamps
from timestamps import transcribe_and_create_timestamps
from collections import defaultdict
from google_drive import google_login
from pair_assets import pair_assets
import json
import os
import shutil

# if os.path.exists("videos"):
#     shutil.rmtree("videos")

if os.path.exists("final_videos"):
    shutil.rmtree("final_videos")

# with open("video_urls.json", "r") as f:
#     url_pairs = json.load(f)

with open("audio_urls.json", "r") as f:
    audio_urls = json.load(f)

with open("vibe_urls.json","r") as f:
    vibe_urls = json.load(f)

google_creds = google_login()

audio_folders = download_assets(audio_urls, "./audio/")
vibe_folders = download_assets(vibe_urls, "./vibes/")

# transcribe_and_create_timestamps(audio_folders)
print(audio_folders)
asset_pairs = pair_assets(audio_folders, vibe_folders)

for index, asset_pair in enumerate(asset_pairs):
    print("asset_pair", asset_pair)
    processed_clips = process_asset_pair_with_timestamps(asset_pair)
    finalize_videos(processed_clips, "final_videos", google_creds, index)


