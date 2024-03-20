from audio_processing import stt, extract_audio
from utils import chunk_list
from parse_interesting_clips import ask_gpt
import json
import os

def transcribe_and_create_timestamps(audio_folders):
    """Create timestamps.json file in each audio folder shaped like so:
    
    Returns: A file containing: [{"timestamps": {"(start, end)": text}}]
    
    """
    print('audio folders', audio_folders)
    for audio_folder in audio_folders:
        print('audio_folder', audio_folder)
        
        asset_file = os.path.join(audio_folder,"asset.mp4")
        stt_path = os.path.join(audio_folder,"stt.json")
        timestamps_output_path = os.path.join(audio_folder, "timestamps.json")

        timestamps = transcribe_audio(asset_file, audio_folder, stt_path)
        chunked_timestamps = chunk_list(timestamps, 500)

        if not os.path.exists(timestamps_output_path):
            print(f"{audio_folder}:  Creating timestamps")
            for i, chunk in enumerate(chunked_timestamps):
                print(f"{audio_folder}:  Parsing for interesting timestamps: {i+1}/{len(chunked_timestamps)}")
                ask_gpt(json.dumps(chunk), timestamps_output_path)
                print("Parsing Complete")
        else:
            print(f"{timestamps_output_path}:  Timestamps already exist, skipping")
        print("Finished creating timestamps")

def transcribe_audio(asset_file, output_folder, stt_path):
    if not os.path.exists(os.path.join(output_folder, "audio.wav")):
        extract_audio(asset_file, output_folder)

    if not os.path.exists(stt_path):
        stt_result = stt(os.path.join(output_folder, "audio.mp3"), stt_path)
        print("Transcribing:", asset_file)
        with open(stt_result, "r") as f:
            timestamps = json.load(f)
    else:
        print(f"{stt_path}: Transcription already exists, accessing existing transcription")
        with open(stt_path, "r") as f:
            timestamps = json.load(f)

    return timestamps