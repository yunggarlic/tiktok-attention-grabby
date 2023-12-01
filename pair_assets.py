import random
import json

def pair_assets(audio_files, vibe_files):
    """Pairs every audio file with every vibe file in different combinations.

    Args:
        audio_files (list): A list of audio files.
        vibe_files (list): A list of vibe files.

    Returns:
        list: A list of dictionaries, each representing a unique combination of audio and vibe files.
    """
    grouped_assets = []
    for audio in audio_files:
        num1 = random.randint(0, len(vibe_files) - 1)
        num2 = random.randint(0, len(vibe_files) - 1)
        while num1 == num2:
            num2 = random.randint(0, len(vibe_files) - 1)
        
        with open(audio + "/" + "metadata.json", "r") as f:
            audio_metadata = json.load(f)
        
        vibe2 = vibe_files[num2] if audio_metadata["has_video"] == False else audio
        videos = [
            {"audio": audio, "vibe": vibe_files[num1], "format": "one_video"},
            {"audio": audio, "vibe": vibe_files[num1], "vibe2": vibe2, "format": "two_video"}
                  ]
        
        num3 = random.randint(0, len(videos) - 1)
        grouped_assets.append(videos[num3])

        
    return grouped_assets