from pytube import YouTube
from pytube.innertube import _default_clients
from concurrent.futures import ThreadPoolExecutor, as_completed
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

def download_asset(asset, output_path):
    print("Initializing Download")
    try:
        yt = YouTube(asset["url"])
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        stream.download(filename="asset.mp4", output_path=output_path)

        with open(output_path + "/" +"metadata.json", "w") as f:
            json.dump(asset, f)
        youtube_id = extract_youtube_id(asset["url"])
        print(f"Downloading Complete || video id:{youtube_id} ")

    except Exception as e:
        print(f"Error downloading video: {e}")
        raise

def download_assets(assets, folder_output):
    asset_paths = []
    with ThreadPoolExecutor(max_workers = 4) as executor:
        future_to_asset = {}
        for asset in assets:
            youtube_id_output_path = os.path.join(folder_output, extract_youtube_id(asset["url"]))

            if not os.path.exists(os.path.join(youtube_id_output_path, 'asset.mp4')): # check for cached videos
                future = executor.submit(download_asset, asset, youtube_id_output_path)
                future_to_asset[future] = youtube_id_output_path
            else:
                print("Asset already downloaded, skipping")
                asset_paths.append(youtube_id_output_path)

        for future in as_completed(future_to_asset):
            try:
                future.result()
                print('appending future to asset', future_to_asset[future])
                asset_paths.append(future_to_asset[future])
            except Exception as e:
                print(f"Error downloading video: {e}")
    
    print("Finished Downloading Assets under ", folder_output)
    return asset_paths

# return a list of folders in the path
def get_local_video_paths(path):
    return [os.path.join(path, folder) for folder in os.listdir(path)]
