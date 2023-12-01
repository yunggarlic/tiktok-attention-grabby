from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, clips_array
from random import uniform
from utils import chunk_list, create_thread, run_threads, create_process, run_processes
from google_drive import upload_file
from skimage.filters import gaussian
import os
import json

def blur(image):
    return gaussian(image.astype(float), sigma=2)

def format_one_video(videos, start=None, stop=None):
    try:
        video = VideoFileClip(videos[0])
        if not start:
            start = video.duration / uniform(1, 2)
        if not stop:
            stop = start + 60
        
        subclip = video.subclip(start, stop)
        subclip_copy = subclip.copy().resize(width=1080, height=960)
        resized_clip = subclip.resize(height=1920)
        
        cropped_clip = resized_clip.crop(x_center=resized_clip.w/2, width=1080, height=1920)
        blurred_clip = cropped_clip.fl_image(blur)
        
        subclip_copy = subclip_copy.set_position(("center","center"))
        composite_clip = CompositeVideoClip([blurred_clip, subclip_copy])
        
        return composite_clip.without_audio()

    except Exception as e:
        print(f"Error processing video: {e}")
        return None

def format_two_videos_column(videos, start=None, stop=None):
    try:
        videos = [VideoFileClip(video) for video in videos]
        if not start:
            start = videos[0].duration / uniform(1, 2)
        if not stop:
            stop = start + 60

        subclips = [video.subclip(start, stop) for video in videos]
        resized_clips = [subclip.resize(height=960) for subclip in subclips]
        cropped_clips = [resized_clip.crop(x_center=resized_clip.w/2, width=1080, height=960) for resized_clip in resized_clips]
        muted_clips = [cropped_clip.without_audio() for cropped_clip in cropped_clips]
        return clips_array([[muted_clips[0]], [muted_clips[1]]])
    except Exception as e:
        print(f"Error processing video: {e}")
        return None    

def extract_audio_track(video, start=None, stop=None):
    try:
        audio = AudioFileClip(video)
        if not start:
            start = audio.duration / uniform(1, 2)
        if not stop:
            stop = start + 60

        subclip = audio.subclip(start, stop)
        return subclip
    except Exception as e:
        print(f"Error extracting audio track: {e}")
        return None

def process_timestamp(timestamp, asset_pair, format_func, timestamped_clip_pairs):
    ts_duration = timestamp["end"] - timestamp["start"]
    print("Timestamp duration: ", ts_duration)
    
    audio_file = asset_pair["audio"] + "/" + "audio.wav"
    vibes = [vibe for vibe in ["vibe", "vibe2"] if vibe in asset_pair.keys()]
    vibe_paths = [asset_pair[vibe] + "/" + "asset.mp4" for vibe in vibes]
    vibe_clips = [VideoFileClip(asset_pair[vibe] + "/" + "asset.mp4") for vibe in vibes]


    min_vibe_duration = max([vibe_clip.duration for vibe_clip in vibe_clips])
    if ts_duration <= min_vibe_duration:
        vibe_start = uniform(0, min_vibe_duration - ts_duration) - 1
        vibe_stop = vibe_start + ts_duration + 1

        timestamped_audio_clip = extract_audio_track(audio_file, start=timestamp["start"], stop=timestamp["end"])
        timestamped_vibe_clip = format_func(videos=vibe_paths, start=vibe_start, stop=vibe_stop)
        
        pair = {"audio": timestamped_audio_clip, "vibe": timestamped_vibe_clip}

        print("Timestamp duration: ", timestamped_audio_clip.duration)
        print("Vibe duration: ", timestamped_vibe_clip.duration)

        if timestamped_audio_clip.duration < 0 or timestamped_audio_clip.duration > 300 or timestamped_vibe_clip.duration < 0:            
            print("Timestamp duration is negative, skipping")
        else:
            timestamped_clip_pairs.append(pair)

    else:
        print("Timestamp duration is longer than vibe duration, skipping")

    for vibe_clip in vibe_clips:
        vibe_clip.close()


    print(len(timestamped_clip_pairs))

def process_asset_pair_with_timestamps(asset_pair):
    process_format = {
        "one_video": format_one_video,
        "two_video": format_two_videos_column
    }
    with open(asset_pair["audio"] + "/" + "timestamps.json", "r") as f:
        timestamps = json.load(f)
    chunked_timestamps = chunk_list(timestamps, 4)
    
    timestamped_asset_pairs = []
    format_func = process_format[asset_pair["format"]]
    for chunk in chunked_timestamps:
        threads = []
        for timestamp in chunk:
            threads.append(create_thread(process_timestamp, (timestamp, asset_pair, format_func, timestamped_asset_pairs)))
        run_threads(threads)
    return timestamped_asset_pairs

def finalize_video(clip_pair, filename, output_path, google_creds):
    print("Finalizing Video: ", filename)
    print("Related Clip Pair: ", clip_pair)
    
    final_video = clip_pair["vibe"].set_audio(clip_pair["audio"])
    full_filename = output_path + "/" + filename
    final_video.write_videofile(full_filename, codec="libx264", audio_codec="aac", fps=24)
    
    for clip in clip_pair.values():
        clip.close()
    final_video.close()
    
    upload_file(full_filename, google_creds)

def finalize_videos(processed_clips, output_path, google_creds, index):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    chunked_clips = chunk_list(processed_clips, 4)
    timestamp_index = 0
    for chunk in chunked_clips:
        processes = []
        for clip_pair in chunk:
            filename = f"final_video_{index}_{timestamp_index}.mp4"
            processes.append(create_process(finalize_video, (clip_pair, filename, output_path, google_creds)))
            timestamp_index += 1

        run_processes(processes)
