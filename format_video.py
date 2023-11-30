from moviepy.editor import VideoFileClip, CompositeVideoClip, clips_array
from random import uniform
from utils import chunk_list, create_thread, run_threads, create_process, run_processes
from google_drive import upload_file
from skimage.filters import gaussian
import os
import json

def blur(image):
    return gaussian(image.astype(float), sigma=2)

def one_video_format(path, mute_audio=False, start=None, stop=None):
    try:
        video_clip = VideoFileClip(path)

        if not start:
            start = video_clip.duration / uniform(1, 2)
        if not stop:
            stop = start + 60

        video_clip = video_clip.subclip(start, stop)

        if mute_audio is True: # this is the vibe clip
            video_clip_copy = video_clip.copy().resize(width=1080)
            resized_clip = video_clip.resize(height=1920)

            cropped_clip = resized_clip.crop(x_center=resized_clip.w/2, width=1080, height=1920)
            cropped_clip = cropped_clip.fl_image(blur)
            
            video_clip_copy = video_clip_copy.set_position(("center","center"))
            composite_clip = CompositeVideoClip([cropped_clip, video_clip_copy])

            return composite_clip.without_audio()
        else:
            return video_clip.audio
    except Exception as e:
        print(f"Error processing video: {e}")
        return None

def two_video_format(path, mute_audio=False, start=None, stop=None):
    try:
        video_clip = VideoFileClip(path)
        if not start:
            start = video_clip.duration / uniform(1, 2)
        if not stop:
            stop = start + 60
        
        video_clip = video_clip.subclip(start, stop)
        resized_clip = video_clip.resize(height=960)
        cropped_clip = resized_clip.crop(x_center=resized_clip.w/2, width=1080, height=960)

        if mute_audio:
            cropped_clip = cropped_clip.without_audio()
        return cropped_clip

    except Exception as e:
        print(f"Error processing video: {e}")
        return None

def process_timestamp(timestamp, path_to_content,path_to_vibe,i, format_func, timestamped_clip_pairs):
    ts_duration = timestamp["end"] - timestamp["start"]

    vibe_duration = VideoFileClip(path_to_vibe).duration
    print(f"Processing timestamp {i} with duration {ts_duration} and vibe duration {vibe_duration}")

    if ts_duration <= vibe_duration:
        vibe_start = uniform(0, vibe_duration - ts_duration) - 1
        vibe_stop = vibe_start + ts_duration + 1

        timestamped_content_clip = format_func(path=path_to_content, mute_audio=False, start=timestamp["start"]-1, stop=timestamp["end"]+1)
        timestamped_vibe_clip = format_func(path=path_to_vibe, mute_audio=True, start=vibe_start, stop=vibe_stop)

        print(f"Timestamped content clip duration: {timestamped_content_clip.duration}")
        print(f"Timestamped vibe clip duration: {timestamped_vibe_clip.duration}")
        if timestamped_content_clip.duration < 0 or timestamped_vibe_clip.duration < 0 or timestamped_content_clip.duration > 300:            
            print("Timestamp duration is negative, skipping")
        else:
            timestamped_clip_pairs.append({"pair":{"content_url": timestamped_content_clip, "vibe_url": timestamped_vibe_clip}})

    else:
        print("Timestamp duration is longer than vibe duration, skipping")


    print(len(timestamped_clip_pairs))

def process_content_clip_timestamps(clip_obj, folder_path):
    process_format = {
        "one_video": one_video_format,
        "two_video": two_video_format
    }
    # For every timestamp, process a subclip of the content video
    with open(folder_path + "/timestamps.json", "r") as f:
        timestamps = json.load(f)["timestamps"]

    format_func = process_format[clip_obj["format"]]

    timestamped_clip_pairs = []
    path_to_content = folder_path + "/" + clip_obj["content_url"]
    path_to_vibe = folder_path + "/" + clip_obj["vibe_url"]

    chunked_timestamps = chunk_list(timestamps, 4)

    for chunk in chunked_timestamps:
        threads = []
        for i, timestamp in enumerate(chunk):
            threads.append(create_thread(process_timestamp, (timestamp, path_to_content, path_to_vibe, i, format_func, timestamped_clip_pairs)))
        run_threads(threads)

    for processed_pair in timestamped_clip_pairs:
        processed_pair["form"] = clip_obj["format"]

    return timestamped_clip_pairs

def finalize_video(clip_pair, format, filename, output_path, google_creds):
    if format == "two_video":
        final_video = clips_array([[clip_pair["content_url"]], [clip_pair["vibe_url"]]])

    elif format == "two_video_reverse":
        final_video = clips_array([[clip_pair["vibe_url"]], [clip_pair["content_url"]]])

    else:
        final_video = clip_pair["vibe_url"]
        final_video = final_video.set_audio(clip_pair["content_url"])
        print("Finalizing Video: ", filename)
        print("Related Clip Pair: ", clip_pair)
        
    full_filename = output_path + "/" + filename
    final_video.write_videofile(full_filename, codec="libx264", audio_codec="aac", fps=24)
    
    for clip in clip_pair.values():
        clip.close()
    final_video.close()
    
    upload_file(full_filename, google_creds)


def finalize_videos(video_index, processed_clips, output_path, google_creds):
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    chunked_clips = chunk_list(processed_clips, 4)
    j = 0
    for chunk in chunked_clips:
        processes = []
        for pair_obj in chunk:
            filename = f"final_video_{video_index}_{j}.mp4"
            clip_pair=pair_obj["pair"]
            format = pair_obj["form"]
            processes.append(create_process(finalize_video, (clip_pair, format, filename, output_path, google_creds)))
            j += 1
        run_processes(processes)