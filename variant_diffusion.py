import torch
import requests
from PIL import Image
from io import BytesIO
from random import randint
from moviepy.editor import ImageSequenceClip
import os
import cv2
import numpy as np
import re
from utils import create_process, run_processes
import shutil

from diffusers import StableDiffusionXLImg2ImgPipeline, AutoPipelineForText2Image

# load the pipeline
device = "cuda"

pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained("stabilityai/stable-diffusion-xl-refiner-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16").to(
    device
)

if os.path.exists("cool"):
    shutil.rmtree("cool")
    os.makedirs("cool")
else:
    os.makedirs("cool")

# let's download an initial image

init_image = Image.open("good-final.png").convert("RGB")
init_image.thumbnail((768, 768))

prompt1 = "growing, vibrant, untouched landscape, growing trees, gently sloping mountains to the left, van gogh, long brush strokes, thick paint application, and a balanced palette of warm, cool and, complementary colors. The scene should be centered, viewed through a single-point perspective, and zoomed in to highlight the lushness of the natural environment."
prompt2 = "farmers working in the foreground. van gogh technique long strokes and thick paint, using warm, complementary colors. centered, single point perspective, zoomed in."
prompt3 = "Illustrate a cozy, small town bustling with people walking together, set against a backdrop of centrally sloping mountains. Adopt van gogh's painting style, characterized by long brush strokes and thick paint in warm, complementary colors. Include trees and a clear blue sky to enhance the scene. Focus on creating a balanced, centered composition."
prompt4 = "Create a close-up scene of people walking together in a quaint, small town. The backdrop should feature mountains sloping towards the center. Use van gogh's painting technique with pronounced long strokes and thick paint application. The color scheme should consist of warm, complementary colors. Ensure the composition is centered."
prompt5 = "semi-agrarian landscape, people walking together in the foreground, sloping mountains in background, van gogh mixed with van gogh, long brush strokes and thick paint in a palette of warm, complementary colors. centered, trees and a blue sky, rural setting"
prompt6 = "old town with people walking in the foreground, buildings and shops in the midground, van gogh, van gogh, long strokes and thick paint application in warm, complementary colors, center sloping mountains, scene focus centered and balanced."
prompt1 = [prompt1] * 500
prompt2 = [prompt2] * 500
prompt3 = [prompt3] * 500
prompt4 = [prompt4] * 500
prompt5 = [prompt5] * 500
prompts = prompt1 + prompt2 + prompt3 + prompt4 + prompt5

negative_prompts = ["wood frame, sex, dark tones, nude"]
print(prompts)

generator = torch.Generator(device=device).manual_seed(3523435)
T = len(prompts) / 55 # period of the sawtooth wave
A = 0.25  # amplitude (half the range of oscillation)
offset = 0.35  # offset for the sine wave

for i, prompt in enumerate(prompts):
    # Calculate the sine wave value for strength
    print(f"Generating image {i}/{len(prompts)}")
    strength = A * np.sin(2 * np.pi * i / T) + offset if i > 0 else 0.95
    print(f"Strength: {strength}")

    conditional = i % 10 == 0

    # Your image generation code
    images = pipe(prompt=prompt, image=init_image, num_inference_steps=150, strength=strength, guidance_scale=7.5, generator=generator, num_images_per_prompt=1).images
    images[0].save(f"cool/{i}_fantasy_landscape.png")
    init_image = images[0]
                            
def interpolate_frames(frame1, frame2):
    print("Interpolating frames")
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    height, width = gray1.shape
    flow_map = np.column_stack((flow[..., 0].flatten(), flow[..., 1].flatten()))

    interpolated = np.zeros_like(frame1)
    for y in range(height):
        for x in range(width):
            fx, fy = flow_map[y * width + x]
            new_x, new_y = min(width - 1, max(0, int(x + fx / 2))), min(height - 1, max(0, int(y + fy / 2)))
            interpolated[y, x] = frame1[new_y, new_x]

    return interpolated


folder_path = "cool/"

# Load images
def extract_number(filename):
    match = re.search(r'^(\d+)', filename)
    return int(match.group()) if match else 0

folder_path = 'cool/'
image_files = sorted(
    [os.path.join(folder_path, img) for img in os.listdir(folder_path) if img.endswith(('.png', '.jpg', '.jpeg'))],
    key=lambda x: extract_number(os.path.basename(x))
)
frames = [cv2.imread(file) for file in image_files]

# Interpolate frames
# output_frames = []
# for i in range(len(frames) - 1):
#     output_frames.append(frames[i])
#     print(f"Triple interpolating frame: {i}/{len(frames) -1}")
#     middle_interpolated_frame = interpolate_frames(frames[i], frames[i + 1])
#     # start_interpolated_frame = interpolate_frames(frames[i], middle_interpolated_frame)
#     # end_interpolated_frame = interpolate_frames(middle_interpolated_frame, frames[i + 1])
#     # output_frames.append(start_interpolated_frame)
#     output_frames.append(middle_interpolated_frame)
#     # output_frames.append(end_interpolated_frame)
# output_frames.append(frames[-1])

# Convert frames for moviepy
moviepy_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames]

# Create and export the video
clip = ImageSequenceClip(moviepy_frames, fps=12)  # Higher fps for smoother playback
files_in_folder = len(os.listdir("vibes/diffusion_animations"))

os.makedirs(f"vibes/diffusion_animations/da_{files_in_folder}")
clip.write_videofile(f"vibes/diffusion_animations/da_{files_in_folder}/asset.mp4", codec="libx264")