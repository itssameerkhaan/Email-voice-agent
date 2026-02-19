# 📧 Voice-Controlled Email Assistant  
### LangGraph | Gemini API | Gmail API | Offline Speech Recognition

An AI-powered **Voice-Based Email Retrieval Assistant** that allows users to interact with their Gmail inbox using natural voice commands.

This system combines:

- Offline Speech-to-Text (Parakeet)
- Large Language Models (Gemini)
- Gmail API Integration
- Agent-based Workflow (LangGraph)
- Text-to-Speech Response (pyttsx3)

Users can retrieve emails simply by speaking commands such as:

> "Show me 5 emails from Faisal received yesterday"

---

## 🚀 Key Features

- 🎤 Offline Voice Input Processing
- 🧠 Natural Language Query Understanding
- 📬 Gmail Inbox Integration
- 📅 Date-Based Email Filtering
- 🔁 Agent Workflow using LangGraph
- 🔊 Spoken Summary of Retrieved Emails
- ⚙️ JSON-Based Filter Extraction using LLM
- 🔐 Secure API Integration using Environment Variables

---

## 🧠 System Architecture

<img width="538" height="687" alt="image" src="https://github.com/user-attachments/assets/db1d09c3-8462-4240-b68f-cd0dba867c1f" />


---

## 📂 Project Structure

<img width="854" height="626" alt="image" src="https://github.com/user-attachments/assets/f8383c5a-3c80-4fc3-8751-5dd8f2c2736b" />




---

## ⚙️ Installation & Setup

Follow the steps below to run this project locally.

---

1️⃣ Clone the Repository

git clone https://github.com/your-username/email-voice-agent.git
cd email-voice-agent


2️⃣ Create Virtual Environment
python -m venv myenv


Activate:

myenv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Setup Gemini API Key

Create a new file in the root directory:

.env


Add:

GEMINI_API_KEY=your_api_key_here

5️⃣ Setup Gmail API

Go to:

https://console.cloud.google.com/

Enable Gmail API

Create OAuth Client ID

Download credentials.json

Place inside:

main/


Run once:

python main/test_gmail_api.py


Login with your Gmail account.

This will automatically create:

token.json

6️⃣ Setup Offline Speech Model (Parakeet)

Run the following command:

python train_parkeet.py


This will automatically:

Download required speech model

Create cache directory

Enable offline speech-to-text

Generated directory:

parakeet_model/cache/


Do not delete this folder after setup.

7️⃣ Run the Email Agent
python main/workflow.py

🎤 Usage

Place a recorded .mp3 voice query inside:

audio/


Example:

"Give me 5 emails from Sameer about project update received yesterday"

The system will:

Process voice input

Understand the request

Retrieve emails

Generate spoken summary

Output saved at:

response/response.mp3

📦 Dependencies

langgraph

google-generativeai

python-dotenv

pyttsx3

SpeechRecognition

pandas

google-api-python-client

google-auth-oauthlib

Install using:

pip install -r requirements.txt

🔐 Security Notice

The following files are excluded using .gitignore:

.env
token.json
credentials.json
parakeet_model/cache/
audio/
audio_backup/
response/


These contain sensitive credentials or large runtime files.

🛠 Future Enhancements

Local LLM Routing (Qwen / DeepSeek)

Email Sending Support

Web Interface Integration

Docker Deployment

Real-Time Microphone Input



Sameer Khan
AI Developer | LangGraph | Voice Agents | Automation
