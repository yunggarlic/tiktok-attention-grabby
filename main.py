from download_video import download_assets, get_local_video_paths
from format_video import finalize_videos, process_asset_pair_with_timestamps
from timestamps import transcribe_and_create_timestamps
from audio_processing import imperceptibly_edit_audio
from collections import defaultdict
from google_drive import google_login
from pair_assets import pair_assets
import json
import os
import shutil
import sys

# Clear out the final videos - we've already uploaded them to Google Drive
if os.path.exists("final_videos"):
    shutil.rmtree("final_videos")

# Load the video URLs that are used as audio and vibe tracks respectively 
with open("audio_urls.json", "r") as f:
    audio_urls = json.load(f)

with open("vibe_urls.json","r") as f:
    vibe_urls = json.load(f)

audio_folders = download_assets(audio_urls, "./audio/")
vibe_folders = download_assets(vibe_urls, "./vibes/") + get_local_video_paths("./vibes/diffusion_animations/")

transcribe_and_create_timestamps(audio_folders)
imperceptibly_edit_audio(audio_folders)
asset_pairs = pair_assets(audio_folders, vibe_folders)

google_creds = google_login()
for index, asset_pair in enumerate(asset_pairs):
    print("asset_pair", asset_pair)
    processed_clips = [clip for clip in process_asset_pair_with_timestamps(asset_pair) if clip is not None]
    finalize_videos(processed_clips, "final_videos", google_creds, index)


