import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip, AudioFileClip, AudioClip
import json
import os
from pydub import AudioSegment
from pydub.generators import WhiteNoise
import sys

def stt(audio_path, t_output):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True, 
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        chunk_length_s=30,
        batch_size=16,
        return_timestamps=True,
        torch_dtype=torch_dtype,
        device=device,
    )    

    result = pipe(audio_path, return_timestamps=True, generate_kwargs={"language": "en"})
    with open(t_output, "w") as f:
        json.dump(result["chunks"], f)

    return t_output
    
def extract_audio(asset_path, output_path):
    print("Extracting audio from", asset_path)
    audio = AudioFileClip(asset_path)
    audio_file_path = os.path.join(output_path, "audio.wav")
    audio.write_audiofile(audio_file_path, codec='pcm_s16le', ffmpeg_params=['-ac', '1'])
    return audio_file_path

def imperceptibly_edit_audio(audio_folders: list[str]):
    [imperceptibly_edit_audio_file(AudioSegment.from_file(os.path.join(audio_path, 'audio.wav')), os.path.join(audio_path, 'audio.wav')) for audio_path in audio_folders]


def imperceptibly_edit_audio_file(audio, audio_path):
    duration = audio.duration_seconds
    

    white_noise = WhiteNoise().to_audio_segment(duration=duration).apply_gain(-70)
    edited_audio = audio.overlay(white_noise, loop=True)    
    edited_audio.invert_phase().export(audio_path, format="wav")

def downsample_audio(audio_path):
    print("Downsampling audio", audio_path)
    original_audio, original_sample_rate = librosa.load(audio_path, sr=None)
    downsampled_audio = librosa.resample(original_audio, orig_sr=original_sample_rate, target_sr=16000)
    sf.write(audio_path, downsampled_audio, 16000)

