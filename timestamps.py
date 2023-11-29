from audio_processing import stt, extract_audio
from utils import chunk_list
from parse_interesting_clips import ask_gpt
import json

def create_timestamps(video_clips):
    for i in video_clips.keys():
        full_video_path = "./videos/videos_" + str(i) + "/" + video_clips[i]["content_url"]
        audio_path = "./videos/videos_" + str(i) + "/audio.wav"
        stt_path = "./videos/videos_" + str(i) + "/stt.json"
        timestamps_path = "./videos/videos_" + str(i) + "/timestamps.json"
        
        with open(stt(extract_audio(full_video_path, audio_path), stt_path), "r") as f:
            timestamps = json.load(f)

        chunked_timestamps = chunk_list(timestamps, 100)
        for chunk in chunked_timestamps:
            ask_gpt(json.dumps(chunk), timestamps_path)
