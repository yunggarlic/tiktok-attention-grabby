import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip

def stt(audio_path, chunk_duration=10):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype= torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
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
        device=device
    )

    dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
    
    result = pipe(audio_path)
    print(result["text"])

def extract_audio(video_path, i):
    full_video_path = "./videos_" + str(i) + "/" + video_path
    video = VideoFileClip(full_video_path)
    
    audio_path = "./videos_" + str(i) + "/audio.wav"
    video.audio.write_audiofile(audio_path, codec='pcm_s16le', ffmpeg_params=['-ac', '1'])
    return audio_path

def downsample_audio(audio_path):
    original_audio, original_sample_rate = librosa.load(audio_path, sr=None)
    downsampled_audio = librosa.resample(original_audio, orig_sr=original_sample_rate, target_sr=16000)
    sf.write(audio_path, downsampled_audio, 16000)

