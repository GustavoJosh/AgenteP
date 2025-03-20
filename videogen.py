import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class VideoGenerator:
    """
    Base class for video generation services
    """
    def generate(self, script, title):
        raise NotImplementedError("Subclasses must implement this method")

class RunwayMLGenerator(VideoGenerator):
    """
    Generate videos using Runway ML's API
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.runwayml.com/v1"
        
    def generate(self, script, title):
        # This is a simplified example - the actual API parameters may differ
        endpoint = f"{self.base_url}/text-to-video"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": script,
            "length": 5  # Generate a 5-second video
        }
        
        response = requests.post(endpoint, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("video_url")
        else:
            raise Exception(f"Failed to generate video: {response.text}")

class DIDGenerator(VideoGenerator):
    """
    Generate videos using D-ID's API (digital avatars with text-to-speech)
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.d-id.com"
    
    def generate(self, script, title):
        # Create a talking avatar video
        endpoint = f"{self.base_url}/talks"
        
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "script": {
                "type": "text",
                "input": script
            },
            "presenter_id": "amy",  # Example presenter ID
            "driver_id": "basic"
        }
        
        # Create the video job
        response = requests.post(endpoint, headers=headers, json=payload)
        
        if response.status_code != 201:
            raise Exception(f"Failed to start video generation: {response.text}")
        
        job_id = response.json().get("id")
        
        # Poll for job completion
        status_endpoint = f"{self.base_url}/talks/{job_id}"
        
        while True:
            status_response = requests.get(status_endpoint, headers=headers)
            status = status_response.json()
            
            if status.get("status") == "done":
                return status.get("result_url")
            
            if status.get("status") == "error":
                raise Exception(f"Video generation failed: {status.get('error')}")
            
            time.sleep(5)  # Wait before polling again

class LocalFFmpegGenerator(VideoGenerator):
    """
    Generate basic videos locally using FFmpeg and text-to-speech
    This doesn't require external APIs but produces simpler videos
    """
    def __init__(self, output_dir="./videos"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if ffmpeg is installed
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("FFmpeg is not installed or not in PATH")
    
    def generate(self, script, title):
        import subprocess
        import gtts
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        import uuid
        
        # Generate a unique ID for this video
        video_id = str(uuid.uuid4())
        safe_title = "".join(c for c in title if c.isalnum() or c in [' ', '_']).strip()
        safe_title = safe_title.replace(' ', '_')
        
        # Create paths for temporary files
        audio_path = os.path.join(self.output_dir, f"{video_id}_audio.mp3")
        images_dir = os.path.join(self.output_dir, f"{video_id}_frames")
        os.makedirs(images_dir, exist_ok=True)
        video_path = os.path.join(self.output_dir, f"{safe_title}_{video_id}.mp4")
        
        # Generate audio from script using gTTS
        tts = gtts.gTTS(script)
        tts.save(audio_path)
        
        # Get audio duration using ffprobe
        duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ]
        duration = float(subprocess.run(
            duration_cmd, capture_output=True, text=True, check=True
        ).stdout.strip())
        
        # Create frames with text
        lines = textwrap.wrap(script, width=40)
        num_frames = 30 * int(duration)  # 30 fps
        
        for i in range(num_frames):
            # Create a blank image
            img = Image.new('RGB', (1280, 720), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Add title
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                font = ImageFont.load_default()
            
            draw.text((640, 100), title, font=font, fill=(255, 255, 255), anchor="mm")
            
            # Add script text (one line at a time, centered)
            y_position = 300
            for line in lines:
                draw.text((640, y_position), line, font=font, fill=(255, 255, 255), anchor="mm")
                y_position += 50
            
            # Save frame
            img.save(os.path.join(images_dir, f"frame_{i:04d}.png"))
        
        # Combine frames and audio into video using ffmpeg
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "30", "-i", 
            os.path.join(images_dir, "frame_%04d.png"),
            "-i", audio_path, "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", video_path
        ]
        
        subprocess.run(ffmpeg_cmd, check=True)
        
        # Clean up temporary files
        import shutil
        os.remove(audio_path)
        shutil.rmtree(images_dir)
        
        return video_path

# Factory to get the right generator based on config
def get_video_generator(generator_type="local"):
    if generator_type == "runway":
        api_key = os.getenv("RUNWAY_API_KEY")
        if not api_key:
            raise ValueError("RUNWAY_API_KEY environment variable is not set")
        return RunwayMLGenerator(api_key)
    
    elif generator_type == "did":
        api_key = os.getenv("DID_API_KEY")
        if not api_key:
            raise ValueError("DID_API_KEY environment variable is not set")
        return DIDGenerator(api_key)
    
    elif generator_type == "local":
        return LocalFFmpegGenerator()
    
    else:
        raise ValueError(f"Unknown generator type: {generator_type}")

# Example usage:
if __name__ == "__main__":
    # Choose your generator
    generator = get_video_generator("local")  # Options: "runway", "did", "local"
    
    # Test with a sample script
    script = "This is a test script about video generation. We're creating a simple video with narration."
    title = "Video Generation Test"
    
    try:
        video_path = generator.generate(script, title)
        print(f"Video generated successfully: {video_path}")
    except Exception as e:
        print(f"Failed to generate video: {str(e)}")