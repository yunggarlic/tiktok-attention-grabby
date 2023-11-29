from pytube import YouTube
import threading

def download_video(key, url, index, output_path, folder_output_path, return_dict):
    print("Initializing Download")
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        stream.download(filename=output_path, output_path=folder_output_path)
        if return_dict[index] is None:
            return_dict[index] = { key: output_path }
        else:
            return_dict[index][key] = output_path

        print("Downloading Complete")

    except Exception as e:
        print(f"Error downloading video: {e}")

def download_videos(url_pairs, folder_output_path, video_clips):
    for i in range(len(url_pairs)):
        # for each pair of videos, download them in parallel
        threads = []
        
        for _, (key, value) in enumerate(url_pairs[i].items()):
            # for each video, create a thread to download it
            if key != "content_url" and key != "vibe_url" :
                continue
            else:
                output_name = "video-content.mp4" if key == "content_url" else "crap-content.mp4"
                threads.append(threading.Thread(target=download_video, args=(key, value, i, output_name, folder_output_path  + str(i), video_clips)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()