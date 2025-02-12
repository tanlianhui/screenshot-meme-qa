import cv2
import numpy as np
import yt_dlp
import easyocr
import os
from pprint import pprint
import asyncio
import glob
from database import initialize_image_database, get_or_insert_video_id, save_images_captions
from time import time

# Download YouTube video
def download_youtube_video(video_url, save_path="."):
    try:
        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True, 
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)  # Get metadata without downloading
            file_path = ydl.prepare_filename(info_dict)  # Prepare the file path based on the template
            ydl.download([video_url]) # Download the video
            return os.path.dirname(file_path)
    except: # age restrictions
        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True, 
            'cookiesfrombrowser': ('chrome',) # using cookies from chrome to prevent age restrictions
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)  # Get metadata without downloading
            file_path = ydl.prepare_filename(info_dict)  # Prepare the file path based on the template
            ydl.download([video_url]) # Download the video
            return os.path.dirname(file_path)


initialize_image_database()

reader = easyocr.Reader(['ch_tra', 'en'])
def has_subtitles(frame):
    """Extracts text from the frame and checks if subtitles exist."""
    results = reader.readtext(frame, batch_size=5)

    # If text is detected, return it as a string
    if results:
        return " ".join([text for (_, text, _) in results])  # Join detected text
    return ""

async def process_video(video_path, output_dir):
    """Extracts frames with subtitles asynchronously from a video file."""
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_id = get_or_insert_video_id(video_path)

    output_folder = os.path.join(output_dir, video_name)
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 1  # Frames per second (avoid division by zero)
    duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)  # Video duration in seconds
    zeros = len(str(duration))  # Padding for filenames

    frame_count = 0

    image_data = []
    while cap.isOpened():
        ret, frame = await asyncio.to_thread(cap.read)  # Read frame asynchronously
        if not ret:
            break

        if frame_count % fps == 0:  # Capture every second
            subtitle_text = await asyncio.to_thread(has_subtitles, frame)  # Process subtitles asynchronously
            if subtitle_text:  # Save frame only if it has subtitles
                screenshot_filename = os.path.join(output_folder, f'screenshot_{frame_count // fps:0{zeros}d}s.png')
                await asyncio.to_thread(cv2.imwrite, screenshot_filename, frame)
                image_data.append((screenshot_filename, subtitle_text, video_id))
                print(f"Saved: {screenshot_filename} (Subtitles: {subtitle_text})")

        frame_count += 1

    save_images_captions(image_data)

    cap.release()

async def process_directory(video_dir, output_dir):
    """Finds all video files in a directory and processes them concurrently."""
    video_files = glob.glob(os.path.join(video_dir, "*.mp4"))  # Adjust extension if needed
    tasks = [process_video(video_path, output_dir) for video_path in video_files]
    await asyncio.gather(*tasks)  # Run tasks concurrently

# Screenshot contexts (conversation coherency)
def build_context_dict(directory):
    """List out directory and returns previous and next file dictionary"""
    files = sorted(os.listdir(directory))
        
    # Build the dictionary
    next_dict, prev_dict = {}, {}
    for i, file in enumerate(files):
        if i == 0:
            prev_dict[file] = "START"
        if i == len(files) - 1:  # Last file
            next_dict[file] = "END"
        else:
            prev_dict[files] = file[i - 1]
            next_dict[file] = files[i + 1]

    return prev_dict, next_dict

# Example usage
if __name__ == '__main__':
    # video_url = "https://youtu.be/ijdspfPMzYc?si=D6HI24XkMA0StZC4"  # Replace with the YouTube video URL
    save_path = "./MyGo/"  # Replace with the directory where you want to save the video
    # if not os.path.exists(save_path):
    #     os.makedirs(save_path)
    # video_path = download_youtube_video(video_url, save_path)
    video_path = "./MyGo/"
    start = time()
    asyncio.run(process_directory(video_path, save_path))
    print(time()-start)