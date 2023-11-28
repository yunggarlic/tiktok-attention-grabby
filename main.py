from moviepy.editor import VideoFileClip, clips_array
from download_video import download_videos
from format_video import one_video_format, two_video_format, finalize_video
from collections import defaultdict
import json
import os
import shutil
from audio_processing import stt, extract_audio, downsample_audio

json_file = "video_urls.json"
process_format = {
    "one_video": one_video_format,
    "two_video": two_video_format
}

with open(json_file, "r") as f:
    url_pairs = json.load(f)

output_pairs = [["video-content.mp4", "crap-content.mp4"] for i in range(len(url_pairs))]

video_clips = defaultdict(dict)
download_videos(url_pairs, output_pairs, video_clips)
audio_path = extract_audio(video_clips[0]["content_url"], 0)
stt(audio_path)

# mute_audio = [False, True]
# processed_clips = []

# # Resize and crop each video of each pair
# for i, clip_obj in enumerate(video_clips.values()):
#     cur_format = url_pairs[i]["format"]
#     processed_pair = {}

#     for j, (key, value) in enumerate(clip_obj.items()):
#         # ex: video_0/video-content.mp4
#         if key == "format":
#             continue

#         full_path = "videos_" + str(i) + "/" + value
#         muted = True if key == "vibe_url" else False

#         processed_video = process_format[cur_format](path=full_path, mute_audio=muted)
#         processed_pair[key] = processed_video
#     processed_clips.append({ "pair": processed_pair, "form": cur_format })

# # Process and stack videos
# for i, pair_obj in enumerate(processed_clips):
#     output_path = "final_videos"
#     clip_pair = pair_obj["pair"]
#     cur_format = pair_obj["form"]

#     if not os.path.exists(output_path):
#         os.makedirs(output_path)
    
#     if cur_format == "two_video":
#         final_video = clips_array([[clip_pair["content_url"]], [clip_pair["vibe_url"]]])  # Stacking vertically
#     else:
#         final_video = clip.pair["vibe_url"]
#         final_video = final_video.set_audio(clip.pair["content_url"])

#     final_video.write_videofile(output_path + "/" + f"final_video_{i}.mp4", codec="libx264", audio_codec="aac", fps=24)


# for i in range(len(url_pairs)):
#     shutil.rmtree("videos_" + str(i))
