import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip, AudioFileClip
import json

def stt(audio_path, t_output):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
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

    result = pipe(audio_path, return_timestamps=True)
    with open(t_output, "w") as f:
        json.dump(result["chunks"], f)

    return t_output
    
def extract_audio(asset_path, output_path):
    audio = AudioFileClip(asset_path)
    audio_file_path = output_path + "/" + "audio.wav"
    audio.write_audiofile(audio_file_path, codec='pcm_s16le', ffmpeg_params=['-ac', '1'])
    return audio_file_path

def downsample_audio(audio_path):
    original_audio, original_sample_rate = librosa.load(audio_path, sr=None)
    downsampled_audio = librosa.resample(original_audio, orig_sr=original_sample_rate, target_sr=16000)
    sf.write(audio_path, downsampled_audio, 16000)

