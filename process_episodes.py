from langchain_ollama import ChatOllama
import cv2
import numpy as np
import os
import yt_dlp
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'


# Download YouTube video
def download_youtube_video(video_url, save_path="."):
    ydl_opts = {
        'outtmpl': f'{save_path}/%(title)s.%(ext)s',
        'format': 'best'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)  # Get metadata without downloading
        file_path = ydl.prepare_filename(info_dict)  # Prepare the file path based on the template
        ydl.download([video_url]) # Download the video
        return file_path

# Get screenshots by episodes and timecodes
def has_subtitles(frame):
    # Convert to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Thresholding to get a binary image
    _, binary_frame = cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY_INV)

    # Use pytesseract to detect text
    text = pytesseract.image_to_string(binary_frame)
    return len(text.strip()) > 0

def extract_subtitle_frames_by_seconds(video_path, fps=30):
    """
    Extracts frames with subtitles from the video and saves them in a folder 
    named after the video file (without extension).

    Args:
        video_path (str): Path to the video file.
        fps (int): Frames per second of the video (default is 30 FPS).
    """
    # Extract the directory and filename (without extension) from the video path
    video_dir = os.path.dirname(video_path)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # Create a folder with the video name in the same directory as the video
    output_folder = os.path.join(video_dir, video_name)
    os.makedirs(output_folder, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    screenshot_count = 0
    last_saved_second = -1  # Initialize to ensure the first second can be saved

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate the current time in seconds
        current_second = int(frame_count / fps)

        # Process only if the frame has subtitles and is at least 1 second from the last saved second
        if has_subtitles(frame) and current_second > last_saved_second:
            # Save the frame using the second as part of the filename
            screenshot_filename = os.path.join(output_folder, f'screenshot_{current_second}s.png')
            cv2.imwrite(screenshot_filename, frame)
            print(f"Saved: {screenshot_filename}")
            screenshot_count += 1
            last_saved_second = current_second  # Update the last saved second

        frame_count += 1

    cap.release()
    print(f"Total frames processed: {frame_count}")
    print(f"Total screenshots taken: {screenshot_count}")
    print(f"Screenshots saved in folder: {output_folder}")


# Get captions
def get_caption(img: str) -> str:
    llm = ChatOllama(model='llava')
    caption = llm.invoke("Please find the Traditional Chinese subtitle for this image. Only output the Traditional Chinese characters. If there is no Chinese subtitles found, return 'No caption found!'. The img is:", img)
    return caption

# Deduplicate screenshots with the same caption
def deduplicate_screenshots_by_caption(screenshot_folder):
    pass

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
    video_url = "https://youtu.be/ijdspfPMzYc?si=D6HI24XkMA0StZC4"  # Replace with the YouTube video URL
    save_path = "./MyGo"  # Replace with the directory where you want to save the video
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    video_path = download_youtube_video(video_url, save_path)
    # print(video_path)
    extract_subtitle_frames_by_seconds(video_path)