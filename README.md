# 🤖 J.A.R.V.I.S. - Advanced AI Desktop Assistant

**Developed by: Ahmed Raza**

A futuristic, voice-activated desktop assistant designed to bridge the gap between Large Language Models (LLMs) and local system automation. Built using **Python**, it features a **Dark Mode GUI** (inspired by ChatGPT), real-time internet connectivity, and ultra-fast inference using **Groq LPUs**.

---

## 🚀 Features

* **⚡ Ultra-Fast Brain:** Powered by **Groq API (Llama-3)** for millisecond-latency responses.
* **🗣️ Natural Voice:** Uses **Edge-TTS** (`en-IN-PrabhatNeural`) for a realistic, human-like voice.
* **🌐 Real-Time Search:** Integrated with **Serper API** to fetch live news, stock prices, and weather from Google.
* **🎨 AI Image Generation:** Generates images from text prompts using **HuggingFace Inference APIs**.
* **🧠 Intelligent Routing:** Uses **Cohere API** to decide whether to Chat, Search, or Automate tasks.
* **🖥️ System Automation:** Can open applications, play YouTube videos, and manage windows.
* **🎙️ Multi-Lingual Input:** Supports Hindi & English voice input (`InputLanguage=hi`).
* **🌑 Modern UI:** Custom-built **Tkinter** interface with a responsive, scrollable chat window.

---

## 🛠️ Tech Stack

| Component | Technology / API |
| :--- | :--- |
| **Frontend (GUI)** | Python Tkinter & CustomTkinter |
| **LLM Engine** | Groq API (Llama-3-8b-8192) |
| **Decision/Router** | Cohere API |
| **Search Engine** | Serper.dev (Google Search) |
| **Image Gen** | Hugging Face Diffusers |
| **Text-to-Speech** | Edge-TTS (Microsoft Azure Neural) |
| **Speech-to-Text** | SpeechRecognition Library |

---

## 📂 Project Structure
```text
RAZA-ASSISTANT/
├── .ven/                  # Virtual Environment (Hidden)
├── Backend/               # Core Logic Files
│   ├── Automation.py      # OS Control & Web Automation
│   ├── Chatbot.py         # Groq API Interaction
│   ├── ImageGeneration.py # Hugging Face Logic
│   ├── Model.py           # Decision Making (Cohere)
│   ├── RealtimeSearch.py  # Serper API Logic
│   ├── SpeechToText.py    # Mic Input Handling
│   └── TextToSpeech.py    # Edge-TTS Output
├── Data/                  # Chat Logs & History
├── Frontend/              # User Interface
│   ├── Files/             # Assets (Images/GIFs)
│   └── GUI.py             # Main Entry Point (Run this)
├── .env                   # API Keys (Not uploaded)
├── .gitignore             # Git Configuration
└── Requirements.txt       # Dependencies
```

## ⚙️ Installation & Setup
# 1. Clone the Repository
Bash
git clone [https://github.com/ahmedraza1234567/JarvisAIAssistant.git](https://github.com/ahmedraza1234567/JarvisAIAssistant.git)
cd JarvisAIAssistant

# 2. Create a Virtual Environment (Optional but Recommended)
Bash
python -m venv .venv
Activate:
Windows: .venv\Scripts\activate
Mac/Linux: source .venv/bin/activate

# 3. Install Dependencies
Bash
pip install -r Requirements.txt

# 4. Configure API Keys
# 🔑 Get Your API Keys

To run this project, you need to generate your own API keys from the following websites. Most of them are **Free** for developers!

| Service | Purpose | 🔗 Website Link (Click to Get Key) |
| :--- | :--- | :--- |
| **Groq Cloud** | Ultra-fast LLM (Llama-3) | [Get Groq API Key](https://console.groq.com/keys) |
| **Cohere** | Brain/Routing Logic | [Get Cohere API Key](https://dashboard.cohere.com/api-keys) |
| **Serper.dev** | Google Search Data | [Get Serper API Key](https://serper.dev/) |
| **Hugging Face** | Image Generation | [Get Access Token](https://huggingface.co/settings/tokens) |

> **Note:** After getting the keys, paste them into your `.env` file as shown below.
Create a file named .env in the root directory and add your keys:

# Code snippet
CohereAPIKey=YOUR_COHERE_KEY
GroqAPIKey=YOUR_GROQ_KEY
SerperAPIKey=YOUR_SERPER_KEY
HuggingFaceAPIKey=YOUR_HUGGINGFACE_KEY

# Configuration
Username=Ahmed Raza
Assistantname=Jarvis
InputLanguage=hi
AssistantVoice=en-IN-PrabhatNeural

# ▶️ How to Run
To start the assistant with the Graphical User Interface:

Bash
python Frontend/GUI.py
(Ensure you are in the root directory before running the command).
