from moviepy.editor import VideoFileClip, AudioFileClip, AudioClip, CompositeVideoClip, clips_array, vfx
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from random import uniform
from utils import chunk_list, create_thread, run_threads, create_process, run_processes
from google_drive import upload_file
from skimage.filters import gaussian
import os
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor

def blur(image):
    return gaussian(image.astype(float), sigma=2)

def format_one_video(videos, start, stop):
    try:
        video = VideoFileClip(videos[0])
        if not start:
            start = video.duration / uniform(1, 2)
        if not stop:
            stop = video.duration
        
        subclip = video.subclip(start, stop)
        subclip_copy = subclip.copy().resize(width=1080, height=960)
        resized_clip = subclip.resize(height=1920)
        
        cropped_clip = resized_clip.crop(x_center=resized_clip.w/2, width=1080, height=1920)
        blurred_clip = cropped_clip.fl_image(blur)
        
        subclip_copy = subclip_copy.set_position(("center","center"))
        composite_clip = CompositeVideoClip([blurred_clip, subclip_copy]).without_audio()
        
        return composite_clip

    except Exception as e:
        print(f"Error processing single video: {e}")
        return None

def format_two_videos_column(videos, start, stop):
    try:
        
        videos = [VideoFileClip(video) for video in videos]
        subclips = [video.subclip(start, stop if stop else video.duration) for video in videos]
        # Step 1: Resize to the correct height, maintaining aspect ratio
        resized_clips_height = [subclip.resize(height=960) for subclip in subclips]
        
        # Step 2: Crop or pad to get the desired width, here we assume cropping
        final_clips = [clip.crop(x_center=clip.size[0]/2, width=1080) if clip.size[0] > 1080 else clip.resize(width=1080) for clip in resized_clips_height]
        
        # Optional: Removing audio from the clips
        muted_clips = [clip.without_audio() for clip in final_clips]
        return clips_array([[muted_clips[0]], [muted_clips[1]]])
    except Exception as e:
        print(f"Error processing twovideos column video: {e}")
        return None    

def crop_video(video):
    return video.crop(x_center=video.w/2, width=1080, height=1920)

def extract_audio_track(video, start, stop):
    try:
        return AudioFileClip(video).subclip(start, stop)
    except Exception as e:
        print(f"Error extracting audio track: {e}")
        return None

def process_timestamp(timestamp, asset_pair, format_func, timestamped_clip_pairs):
    print('timestamp',timestamp)
    ts_duration = timestamp["end"] - timestamp["start"]
    print("Timestamp duration: ", ts_duration)
    
    audio_file = os.path.join(asset_pair["audio"], "audio.wav")

    vibes = [vibe for vibe in ["vibe", "vibe2"] if vibe in asset_pair.keys()]
    vibe_paths = [os.path.join(asset_pair[vibe], "asset.mp4") for vibe in vibes]
    vibe_clips = [VideoFileClip((os.path.join(asset_pair[vibe], "asset.mp4"))) for vibe in vibes]

    print('vibe-clips', vibe_clips)

    min_vibe_duration = min([vibe_clip.duration for vibe_clip in vibe_clips])
    print("Min vibe duration: ", min_vibe_duration)
    if ts_duration <= min_vibe_duration:
        vibe_start = uniform(0, min_vibe_duration - ts_duration) - 1
        vibe_stop = vibe_start + ts_duration + 1

        timestamped_audio_clip = extract_audio_track(audio_file, start=timestamp["start"], stop=timestamp["end"])
        timestamped_vibe_clip = format_func(videos=vibe_paths, start=vibe_start, stop=vibe_stop)
        
        if timestamped_vibe_clip is None or timestamped_audio_clip is None:
            print("Error processing timestamp")
            return

        pair = {"audio": timestamped_audio_clip, "vibe": timestamped_vibe_clip}
        print('timestamped vibe clip -->', timestamped_vibe_clip)
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
    with open(os.path.join(asset_pair["audio"], "timestamps.json"), "r") as f:
        timestamps = json.load(f)
    
    print(timestamps)
    timestamped_asset_pairs = []
    format_func = process_format[asset_pair["format"]]
    print("Format Func: ", asset_pair["format"])

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures_to_clips = []
        for timestamp in timestamps:
            future = executor.submit(process_timestamp, timestamp, asset_pair, format_func, timestamped_asset_pairs)
            futures_to_clips.append(future)
        for future in as_completed(futures_to_clips):
            future.result()
            timestamped_asset_pairs.append(future.result())
            
    return timestamped_asset_pairs

def finalize_video(clip_pair, filename, output_path, google_creds):
    print("Finalizing Video: ", filename)
    print("Related Clip Pair: ", clip_pair)

    full_filename = os.path.join(output_path, filename)

    final_video = crop_video(clip_pair["vibe"].set_audio(clip_pair["audio"]).fadeout(duration=1))
    final_video.write_videofile(full_filename, codec="libx264", audio_codec="aac")
    
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
            print('clip --> ',clip_pair)
            filename = f"final_video_{index}_{timestamp_index}.mov"
            processes.append(create_process(finalize_video, (clip_pair, filename, output_path, google_creds)))
            timestamp_index += 1

        run_processes(processes)

