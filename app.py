from flask import Flask, request, url_for, redirect, render_template, jsonify, send_from_directory
import os
from datetime import datetime
import threading
import sys
from flask import jsonify
from datetime import datetime
from flask import send_file

# Add the path to import from workflow.py
sys.path.append(r'D:\langGraph\email_agent\main')
# from workflow import run

app = Flask(__name__)
app.secret_key = "supersecret"

# Create audio folders if they don't exist
AUDIO_FOLDER = r'D:\langGraph\email_agent\audio'
AUDIO_BACKUP_FOLDER = r'D:\langGraph\email_agent\audio_backup'
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(AUDIO_BACKUP_FOLDER, exist_ok=True)

def get_next_query_number():
    """Get the next query number based on existing files in backup folder"""
    try:
        # Get all query files
        query_files = [f for f in os.listdir(AUDIO_BACKUP_FOLDER) if f.startswith('query_')]
        
        if not query_files:
            return 1
        
        # Extract numbers from filenames
        numbers = []
        for filename in query_files:
            try:
                # Extract number from "query_X_timestamp.mp3"
                num = int(filename.split('_')[1])
                numbers.append(num)
            except:
                continue
        
        if numbers:
            return max(numbers) + 1
        else:
            return 1
    except Exception as e:
        print(f"Error getting query number: {e}")
        return 1

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/save-audio", methods=["POST"])
def save_audio():
    try:
        if 'audio' not in request.files:
            print("No audio file in request")
            return jsonify({'error': 'No audio file'}), 400
        
        audio_file = request.files['audio']
        
        # Get current time for backup filename
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get next query number
        query_number = get_next_query_number()
        
        # Filenames
        main_filename = "audio.mp3"  # Always same name in main folder
        backup_filename = f"query_{query_number}_{current_time}.mp3"  # Unique name in backup
        
        # Get the original format from content type
        content_type = audio_file.content_type
        print(f"Received audio content type: {content_type}")
        
        # Determine file extension based on content type
        if 'webm' in content_type:
            temp_filename = f"temp_recording.webm"
        elif 'mp4' in content_type or 'mp4a' in content_type:
            temp_filename = f"temp_recording.m4a"
        elif 'mpeg' in content_type or 'mp3' in content_type:
            temp_filename = f"temp_recording.mp3"
        else:
            temp_filename = f"temp_recording.webm"  # Default
        
        print(f"Saving as: {temp_filename}")
        
        # Save temporary file
        temp_path = os.path.join(AUDIO_FOLDER, temp_filename)
        audio_file.save(temp_path)
        print(f"Temporary file saved: {temp_path}")
        
        # Define final paths
        filepath_main = os.path.join(AUDIO_FOLDER, main_filename)
        filepath_backup = os.path.join(AUDIO_BACKUP_FOLDER, backup_filename)
        
        try:
            from pydub import AudioSegment
            
            # Load audio file
            print("Converting to MP3...")
            audio = AudioSegment.from_file(temp_path)
            
            # Export as MP3 to both locations
            # Main folder: always "audio.mp3" (overwrites existing)
            audio.export(filepath_main, format="mp3", bitrate="192k")
            print(f"Audio saved to main folder: {filepath_main}")
            
            # Backup folder: unique query filename
            audio.export(filepath_backup, format="mp3", bitrate="192k")
            print(f"Audio backup saved: {filepath_backup}")
            
            # Remove temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
        except ImportError:
            print("pydub not available, saving original file")
            # If pydub is not available, just copy the file
            import shutil
            shutil.copy(temp_path, filepath_main)
            shutil.copy(temp_path, filepath_backup)
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as convert_error:
            print(f"Conversion error: {convert_error}")
            # If conversion fails, save the original
            import shutil
            if os.path.exists(temp_path):
                shutil.copy(temp_path, filepath_main)
                shutil.copy(temp_path, filepath_backup)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        return jsonify({
            'success': True, 
            'filename': main_filename,
            'backup_filename': backup_filename,
            'query_number': query_number
        }), 200
    
    except Exception as e:
        print(f"Error saving audio: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route("/get-audio-list")
def get_audio_list():
    try:
        # Get all audio files from backup folder
        audio_files = [f for f in os.listdir(AUDIO_BACKUP_FOLDER) 
                      if f.startswith('query_') and f.endswith(('.mp3', '.webm', '.m4a', '.wav'))]
        # Sort by filename (which includes query number and timestamp)
        audio_files.sort(reverse=True)  # Latest first
        return jsonify({'files': audio_files}), 200
    except Exception as e:
        print(f"Error getting audio list: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/audio/<filename>")
def serve_audio(filename):
    try:
        return send_from_directory(AUDIO_BACKUP_FOLDER, filename)
    except Exception as e:
        print(f"Error serving audio: {e}")
        return jsonify({'error': str(e)}), 404
    

RESPONSE_FILE = r"D:\langGraph\email_agent\response\response.mp3"

@app.route('/check-response')
def check_response():
    if os.path.exists(RESPONSE_FILE):
        ts = int(os.path.getmtime(RESPONSE_FILE))
        return jsonify({"available": True, "timestamp": ts})
    else:
        return jsonify({"available": False})
    
    

@app.route('/get-response')
def get_response():
    return send_file(RESPONSE_FILE, mimetype='audio/mpeg')


# # Function to run the workflow in background
# def run_workflow_background():
#     try:
#         print("Starting workflow watcher...")
#         run()  # This will run the workflow function
#     except Exception as e:
#         print(f"Error in workflow: {e}")
#         import traceback
#         traceback.print_exc()

if __name__ == "__main__":
    # Start the workflow watcher in a separate daemon thread
    # workflow_thread = threading.Thread(target=run_workflow_background, daemon=True)
    # workflow_thread.start()
    # print("Workflow thread started")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)