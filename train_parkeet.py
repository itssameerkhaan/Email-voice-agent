"""
Email Agent with Voice Commands
Using imported Parakeet ASR model
"""

import os
import ffmpeg
import nemo.collections.asr as nemo_asr

# Only define the model if called from main
model = None

def load_model():
    global model
    if model is None:
        os.environ['NEMO_CACHE_DIR'] = r".\parakeet_model\cache"
        model = nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-tdt-0.6b-v2")
        print("Model imported successfully!")
    return model

def get_text():
    try:
        load_model()  # ensure model is loaded

        input_file = r"D:\langGraph\email_agent\audio\Audio.mp3"
        output_file = r"D:\langGraph\email_agent\audio\Audio.wav"

        # Check input exists
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Full path to ffmpeg executable
        ffmpeg_path = r"C:\Users\user\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe"

        # Convert MP3 → WAV
        ffmpeg.input(input_file).output(output_file).run(cmd=ffmpeg_path, overwrite_output=True)
        print("Audio converted to WAV successfully!")

        output = model.transcribe([output_file])
        content = output[0].text
        return content
    except:
        pass

def delete_Audio() -> bool:
    WATCH_FOLDER = r"D:\langGraph\email_agent\audio"
    files = [f for f in os.listdir(WATCH_FOLDER) if os.path.isfile(os.path.join(WATCH_FOLDER, f))]
    for file in files:
        file_path = os.path.join(WATCH_FOLDER, file)
        os.remove(file_path)
        print(f"Deleted file:----- {file}")
    files = [f for f in os.listdir(WATCH_FOLDER) if os.path.isfile(os.path.join(WATCH_FOLDER, f))]
    if not files:
        return True
    else:
        return False

