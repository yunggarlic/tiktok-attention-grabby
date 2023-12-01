from pytube import YouTube
import threading
import re
import json
import os
from utils import chunk_list, run_threads

def extract_youtube_id(url):
    regex = r'(?:v=)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    if match:
       return match.group(1)
    return None

def cache_video(id):
    if not os.path.exists("video_cache.json"):
        with open("video_cache.json", "w") as f:
            json.dump({id: True}, f)
    else:
        with open("video_cache.json", "r") as f:
            cache = json.load(f)
        cache[id] = True
        with open("video_cache.json", "w") as f:
            json.dump(cache, f)

def download_asset(asset, output_path):
    print("Initializing Download")
    try:
        yt = YouTube(asset["url"])
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        stream.download(filename="asset.mp4", output_path=output_path)

        with open(output_path + "/" +"metadata.json", "w") as f:
            json.dump(asset, f)
        youtube_id = extract_youtube_id(asset["url"])

        cache_video(youtube_id)
        print(f"Downloading Complete || video id:{youtube_id} ")

    except Exception as e:
        print(f"Error downloading video: {e}")

def download_assets(assets, folder_output):
    chunk_assets = chunk_list(assets, 4)
    asset_paths = []
    for chunk in chunk_assets:
        threads = []
        for asset in chunk:
            youtube_id_folder_output = folder_output + extract_youtube_id(asset["url"])
            asset["output_path"] = youtube_id_folder_output
            if not os.path.exists(youtube_id_folder_output):  
                threads.append(threading.Thread(target=download_asset, args=(asset, youtube_id_folder_output)))
            else:
                print("Asset already downloaded, skipping")

            asset_paths.append(youtube_id_folder_output)
        run_threads(threads)

    print("Finished Downloading Assets under ", folder_output)

    return asset_paths
