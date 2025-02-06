import cv2
import numpy as np
import yt_dlp
import os
os.environ["OLLAMA_HOST"] = "http://192.168.1.221:11434"
# os.environ['TESSDATA_PREFIX'] = "/opt/homebrew/share/tessdata/"
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
import easyocr

# Download YouTube video
def download_youtube_video(video_url, save_path="."):
    try:
        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'format': 'best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)  # Get metadata without downloading
            file_path = ydl.prepare_filename(info_dict)  # Prepare the file path based on the template
            ydl.download([video_url]) # Download the video
            return file_path
    except: # age restrictions
        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'format': 'best',
            'cookiesfrombrowser': ('chrome',) # using cookies from chrome to prevent age restrictions
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)  # Get metadata without downloading
            file_path = ydl.prepare_filename(info_dict)  # Prepare the file path based on the template
            ydl.download([video_url]) # Download the video
            return file_path

# Get screenshots by episodes and timecodes
def has_subtitles(frame):
    """ Extracts text from the frame and checks if subtitles exist. """
    reader = easyocr.Reader(['ch_tra', 'ch_sim', 'en', 'ja', 'ko'])
    results = reader.readtext(frame)

    # If text is detected, return it as a string
    if results:
        return "".join([text for (_, text, _) in results])
    return ""

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

    prev_frame_caption = ""
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate the current time in seconds
        current_second = int(frame_count / fps)

        # Process only if the frame has subtitles and is at least 1 second from the last saved second
        caption = has_subtitles(frame)
        if prev_frame_caption != caption and caption and current_second > last_saved_second:
            # Save the frame using the second as part of the filename
            screenshot_filename = os.path.join(output_folder, f'screenshot_{current_second}s_{caption}.png')
            cv2.imwrite(screenshot_filename, frame)
            print(f"Saved: {screenshot_filename}")
            screenshot_count += 1
            last_saved_second = current_second  # Update the last saved second
        prev_frame_caption = caption

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
    print(f"Total frames processed: {frame_count}")
    print(f"Total screenshots taken: {screenshot_count}")
    print(f"Screenshots saved in folder: {output_folder}")


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
    # save_path = "./MyGo"  # Replace with the directory where you want to save the video
    # if not os.path.exists(save_path):
    #     os.makedirs(save_path)
    # video_path = download_youtube_video(video_url, save_path)
    video_path = "./MyGo/BanG Dream! It's MyGO!!!!! 第04話【一輩子喔！？】｜Muse木棉花 動畫 線上看.mp4"
    print(video_path)
    extract_subtitle_frames_by_seconds(video_path)