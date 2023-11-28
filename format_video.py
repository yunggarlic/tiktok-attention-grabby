from moviepy.editor import VideoFileClip, AudioFileClip
from audio_processing import stt, downsample_audio
from random import uniform


def one_video_format(path, mute_audio=False, start=None, stop=None):
    try:
        video_clip = VideoFileClip(path)

        if not start:
            start = video_clip.duration / uniform(1, 2)
        if not stop:
            stop = start + 60

        video_clip = video_clip.subclip(start, stop)

        if mute_audio is True:
            resized_clip = video_clip.resize(height=1920)
            cropped_clip = resized_clip.crop(x_center=resized_clip.w/2, width=1080, height=1920)
            return cropped_clip.without_audio()
        else:
            return video_clip.audio
    except Exception as e:
        print(f"Error processing video: {e}")
        return None

def two_video_format(path, mute_audio=False, start=None, stop=None):
    print(path)
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

def finalize_video(video_clips, output_path):
    final_video = clips_array([[clip] for clip in video_clips])  # Stacking vertically
    final_video.write_videofile(output_path + "/" + "final_video.mp4", codec="libx264", audio_codec="aac", fps=24) 