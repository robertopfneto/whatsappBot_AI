import os
import requests
import mimetypes
from subprocess import run
from identify import process_video

VIDEOS_DIR = 'videos_download'

def clean_videos_directory():
    """Remove all files in the videos_download directory."""
    for filename in os.listdir(VIDEOS_DIR):
        file_path = os.path.join(VIDEOS_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")

def download_video(media_url, filename):
    try:
        print(f"Downloading video from {media_url}")  

        auth = (os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

        video_response = requests.get(media_url, stream=True, auth=auth)
        video_response.raise_for_status() 
        with open(filename, 'wb') as video_file:
            for chunk in video_response.iter_content(chunk_size=8192):
                video_file.write(chunk)

        print(f"Video downloaded successfully: {filename}")  
        return True
    except Exception as e:
        print(f"Error downloading video: {e}")  
        return False

def process_whatsapp_video(media_url, from_number):
    video_filename = os.path.join(VIDEOS_DIR, "received_video.mp4")

    if not download_video(media_url, video_filename):
        print("Failed to download video.")
        return

    mime_type, _ = mimetypes.guess_type(video_filename)
    if mime_type and mime_type.startswith('video/mp4'):
        video_filename = fix_video(video_filename)
        if video_filename is None:
            print("Failed to repair video.")
            return
    else:
        converted_filename = os.path.join(VIDEOS_DIR, "converted_video.mp4")
        try:
            if not convert_video(video_filename, converted_filename):
                print("Error converting video.")
                return
            video_filename = converted_filename
        except Exception as e:
            print(f"Error converting video: {e}")  
            return

    process_video(video_filename, from_number)

def process_youtube_video(youtube_url, from_number):
    print(f"Received YouTube URL: {youtube_url}")  

    try:

        import yt_dlp
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join(VIDEOS_DIR, 'youtube_video.mp4'),
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        video_filename = os.path.join(VIDEOS_DIR, 'youtube_video.mp4')
        print(f"Video downloaded successfully: {video_filename}")  

        fixed_filename = fix_video(video_filename)
        if fixed_filename is None:
            print("Failed to repair video.")
            return

        process_video(fixed_filename, from_number)
    
    except Exception as e:
        print(f"Error processing YouTube video: {e}")  

def convert_video(input_filename, output_filename):
    print(f"Converting video: {input_filename} to {output_filename}")  
    try:
        command = [
            'ffmpeg',
            '-i', input_filename,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_filename
        ]
        result = run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Video converted successfully: {output_filename}")  
            return True
        else:
            print(f"Error converting video: {result.stderr}")  
            return False
    except Exception as e:
        print(f"Error executing ffmpeg: {e}")  
        return False

def fix_video(input_filename):
    output_filename = os.path.join(VIDEOS_DIR, "fixed_" + os.path.basename(input_filename))
    print(f"Attempting to repair video: {input_filename} to {output_filename}")  
    try:
        command = [
            'ffmpeg',
            '-i', input_filename,
            '-c', 'copy',
            output_filename
        ]
        result = run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Video repaired successfully: {output_filename}")  
            return output_filename
        else:
            print(f"Error repairing video: {result.stderr}")  
            return None
    except Exception as e:
        print(f"Error executing ffmpeg for repair: {e}")  
        return None
