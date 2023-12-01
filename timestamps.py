from audio_processing import stt, extract_audio
from utils import chunk_list
from parse_interesting_clips import ask_gpt
import json
import os

def transcribe_and_create_timestamps(audio_folders):
    """Create timestamps.json file in each audio folder shaped like so:
    
    Returns: A file containing: [{"timestamps": {"(start, end)": text}}]
    
    """
    for audio_folder in audio_folders:
        asset_file = audio_folder + "/" + "asset.mp4"
        stt_path = audio_folder + "/" + "stt.json"
        timestamps_output_path = audio_folder + "/" + "timestamps.json"

        timestamps = transcribe_audio(asset_file, audio_folder, stt_path)
        chunked_timestamps = chunk_list(timestamps, 100)

        for i, chunk in enumerate(chunked_timestamps):
            print(f"Parsing for interesting timestamps: {i+1}/{len(chunked_timestamps)}")
            ask_gpt(json.dumps(chunk), timestamps_output_path)
            print("Parsing Complete")
        print("Finished creating timestamps")

def transcribe_audio(asset_file, output_folder, stt_path):
    if not os.path.exists(stt_path):
        stt_result = stt(extract_audio(asset_file, output_folder), stt_path)
        print("Transcribing:", asset_file)
        with open(stt_result, "r") as f:
            timestamps = json.load(f)
    else:
        print("Transcription already exists, accessing existing transcription")
        with open(stt_path, "r") as f:
            timestamps = json.load(f)

    return timestamps
        