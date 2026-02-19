from flask import Flask, request, jsonify, render_template_string
import base64
import os
from datetime import datetime

app = Flask(__name__)

# Create directory for audio files if it doesn't exist
AUDIO_DIR = "audio"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def save_audio(base64data):
    try:
        # Extract base64 data (remove data URL prefix)
        if ',' in base64data:
            audio_bytes = base64.b64decode(base64data.split(',')[1])
        else:
            audio_bytes = base64.b64decode(base64data)
        
        # Create filename with timestamp
        
        filename = f"{AUDIO_DIR}/Audio.mp3"
        
        with open(filename, "wb") as f:
            f.write(audio_bytes)
        
        print(f"🎤 Audio saved as {filename}")
        return {"status": "success", "filename": filename}
    
    except Exception as e:
        print(f"Error saving audio: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Audio Recorder</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
        }
        #dots {
            display: inline-block;
            margin-left: 10px;
        }
        .dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            margin: 0 2px;
            background-color: red;
            border-radius: 50%;
            opacity: 0.3;
            transform: translateY(0px);
            animation: bounce 1s infinite;
        }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: translateY(0px); opacity: 0.3; }
            40% { transform: translateY(-10px); opacity: 1; }
        }
        
        button {
            padding: 20px;
            font-size: 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        button:active {
            transform: scale(0.98);
        }
        
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🎙️ Audio Recorder</h1>
    <p>Hold the button to record, release to save</p>
    
    <button id="recbtn">🎙️ Hold to Record</button>
    <div id="dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
    </div>
    
    <audio id="player" controls style="margin-top: 20px;"></audio>
    
    <div id="status"></div>
    
    <script>
        let mediaRecorder;
        let audioChunks = [];
        const recbtn = document.getElementById('recbtn');
        const dots = document.getElementById('dots');
        const statusDiv = document.getElementById('status');
        const player = document.getElementById('player');
        
        dots.style.visibility = 'hidden';

        function showStatus(message, isError = false) {
            statusDiv.textContent = message;
            statusDiv.className = `status ${isError ? 'error' : 'success'}`;
            setTimeout(() => {
                statusDiv.textContent = '';
                statusDiv.className = '';
            }, 3000);
        }

        recbtn.onmousedown = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        sampleRate: 44100
                    } 
                });
                
                mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm;codecs=opus'
                });
                
                audioChunks = [];
                mediaRecorder.start(100); // Collect data every 100ms
                dots.style.visibility = 'visible';
                recbtn.textContent = '🔴 Recording...';
                recbtn.style.background = 'linear-gradient(45deg, #ff4757, #ff3838)';
                
                mediaRecorder.ondataavailable = e => {
                    if (e.data.size > 0) {
                        audioChunks.push(e.data);
                    }
                };
                
            } catch (err) {
                showStatus('Error accessing microphone: ' + err.message, true);
                console.error('Microphone access error:', err);
            }
        };

        recbtn.onmouseup = () => {
            if (!mediaRecorder) return;
            
            mediaRecorder.stop();
            dots.style.visibility = 'hidden';
            recbtn.textContent = '🎙️ Hold to Record';
            recbtn.style.background = 'linear-gradient(45deg, #ff6b6b, #ee5a52)';
            
            mediaRecorder.onstop = async () => {
                try {
                    if (audioChunks.length === 0) {
                        showStatus('No audio recorded', true);
                        return;
                    }
                    
                    const blob = new Blob(audioChunks, { type: 'audio/webm' });
                    const reader = new FileReader();
                    reader.readAsDataURL(blob);
                    
                    reader.onloadend = async function() {
                        const base64data = reader.result;
                        
                        // Send to server
                        const response = await fetch('/save_audio', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({audio_data: base64data})
                        });
                        
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            showStatus(`Audio saved: ${result.filename}`);
                            // Set player source
                            player.src = URL.createObjectURL(blob);
                            player.style.display = 'block';
                        } else {
                            showStatus(`Error: ${result.message}`, true);
                        }
                    };
                    
                } catch (err) {
                    showStatus('Error processing audio: ' + err.message, true);
                    console.error('Audio processing error:', err);
                }
            };
        };

        // Prevent recording on touch devices
        recbtn.ontouchstart = (e) => {
            e.preventDefault();
            recbtn.onmousedown();
        };

        recbtn.ontouchend = (e) => {
            e.preventDefault();
            recbtn.onmouseup();
        };
    </script>
</body>
</html>
    """)

@app.route('/save_audio', methods=['POST'])
def save_audio_endpoint():
    try:
        data = request.get_json()
        base64data = data.get('audio_data')
        
        if not base64data:
            return jsonify({"status": "error", "message": "No audio data received"}), 400
        
        result = save_audio(base64data)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🎙️ Audio Recorder Server Starting...")
    print(f"📁 Audio files will be saved to: {os.path.abspath(AUDIO_DIR)}")
    app.run(debug=True, host='0.0.0.0', port=5000)