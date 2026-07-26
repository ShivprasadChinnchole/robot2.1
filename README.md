# 🤖 AURA — AI-based Automated University Response Assistant



**Built by SAD Group — Shiv | Akshata | Diksha**
**CSE IoT CSBT Department | VIT Pune Kondhwa Campus**



---

## 📌 What is AURA?

AURA is an **edge-deployed AI voice assistant robot** built for the CSE IoT CSBT Department at VIT Pune Kondhwa Campus. It serves as an intelligent department receptionist that answers student and parent queries about faculty, labs, syllabus, achievements, research, and events — using voice interaction.

AURA runs entirely on a **Raspberry Pi Zero 2W** with just 512MB RAM, making it a true edge AI deployment.

---

## 🎯 Problem Statement

Traditional department reception desks face:
- Repetitive queries about faculty, labs, syllabus, and events
- No 24/7 availability for student information
- Human resource inefficiency for routine Q&A
- Language and accessibility barriers

**AURA solves all of this with a smart AI voice assistant.**

---

## ✨ Features

- 🎤 **Voice Input** — 6-second recording window using arecord
- 🧠 **RAG Pipeline** — BM25 retrieval over 108 domain-specific chunks
- 🤖 **LLM Answer Generation** — Groq LLaMA 3.3 70B Versatile
- 🔊 **Indian English TTS** — gTTS with co.in locale via Bluetooth speaker
- 💤 **Wake/Sleep Mode** — State machine with 30-second timeout
- 🗺️ **Guided Tour Mode** — 10-point department overview (zero tokens)
- 🔄 **Auto Start on Boot** — systemd service for real robot deployment
- 📚 **27,000+ character** domain-specific knowledge base

---

## 🏗️ System Architecture

```
User speaks
    ↓
arecord (44100Hz WAV capture)
    ↓
Google Speech Recognition (en-IN)
    ↓
is_guided_tour_request() check
    ↓ YES                    ↓ NO
Pre-written tour         BM25 + Query Expansion
(0 tokens used)               ↓
                    Top 3 relevant chunks
                              ↓
                    Groq LLaMA 3.3 70B
                    (max_tokens=80)
                              ↓
                    Humanizer text processing
                              ↓
                    gTTS Indian English MP3
                              ↓
                    mpg123 → Bluetooth Speaker
```

---

## 🔧 Hardware Requirements

| Component | Specification |
|---|---|
| Microcontroller | Raspberry Pi Zero 2W |
| Microphone | Zebronics ZEB-Klarity USB |
| Speaker | Bluetooth A2DP Speaker |
| Storage | MicroSD Card (16GB+) |
| OS | Raspberry Pi OS Lite 32-bit |
| Power | 5V 2.5A micro USB |

---

## 💻 Software Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Audio Capture | arecord (ALSA native) |
| Speech to Text | Google Speech Recognition (en-IN) |
| Search Engine | BM25Okapi (rank-bm25) |
| LLM | Groq API — LLaMA 3.3 70B Versatile |
| Text to Speech | gTTS (Indian English) |
| Audio Playback | mpg123 |
| Bluetooth | PulseAudio + BlueZ |

---

## 📁 Project Structure

```
robot_assistant/
├── voice_chat.py          ← Main application — voice pipeline + state machine
├── config.py              ← API keys configuration
├── brain/
│   └── query_handler.py   ← RAG brain — BM25 + Groq LLM pipeline
├── database/
│   └── dept_knowledge.txt ← Department knowledge base (27,000+ chars)
├── start_aura.sh          ← Auto-start shell script
└── README.md              ← This file
```

---

## ⚙️ Installation

### Step 1 — Flash Raspberry Pi OS
Flash **Raspberry Pi OS Lite 32-bit** using Raspberry Pi Imager with:
- WiFi SSID and password configured
- SSH enabled
- Hostname: `shiv`

### Step 2 — SSH into Pi
```bash
ssh sad@shiv.local
```

### Step 3 — Clone the repository
```bash
cd /home/sad
git clone https://github.com/ShivprasadChinnchole/AURA.git robot_assistant
cd robot_assistant
```

### Step 4 — Create virtual environment
```bash
python3 -m venv robot_env
source robot_env/bin/activate
```

### Step 5 — Install system dependencies
```bash
sudo apt install -y pulseaudio pulseaudio-module-bluetooth bluez \
python3-pip portaudio19-dev flac mpg123 espeak libopenblas-dev \
python3-numpy paxctl binutils git
```

### Step 6 — Install Python dependencies
```bash
pip install pyaudio SpeechRecognition groq rank_bm25 numpy colorama gtts setuptools
```

### Step 7 — Configure API keys
```bash
nano config.py
```
Add your Groq API key:
```python
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL = "llama-3.3-70b-versatile"
```

### Step 8 — Configure Bluetooth
```bash
bluetoothctl
scan on
# Find your speaker MAC address
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
exit
```

### Step 9 — Run AURA
```bash
python3 voice_chat.py
```

---

## 🚀 Auto Start on Boot (Real Robot Mode)

### Create systemd service
```bash
sudo nano /etc/systemd/system/aura.service
```

Paste:
```
[Unit]
Description=AURA AI Robot Assistant
After=network.target bluetooth.target sound.target

[Service]
Type=simple
User=sad
WorkingDirectory=/home/sad/robot_assistant
ExecStart=/home/sad/robot_assistant/start_aura.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable service
```bash
sudo systemctl daemon-reload
sudo systemctl enable aura.service
sudo systemctl start aura.service
```

Now AURA starts automatically every time Pi boots! 🎉

---

## 🗣️ How to Use

| Command | Action |
|---|---|
| Speak naturally | AURA listens for 6 seconds |
| `"wake up aura"` | Wake AURA from sleep mode |
| `"sleep aura"` | Put AURA into sleep mode |
| `"stop"` / `"stop aura"` | Stop current response |
| `"guide me"` | Get full 10-point department tour |
| `"who is HOD"` | Faculty information |
| `"where is IoT lab"` | Lab location |
| `"tell me about semester 4"` | Syllabus information |

---

## 🧠 RAG Pipeline Details

### BM25 Algorithm
```
Score(D,Q) = Σ IDF(qi) × [f(qi,D) × (k1+1)] / [f(qi,D) + k1×(1-b+b×|D|/avgdl)]
```
- k1 = 1.5 (term saturation)
- b = 0.75 (length normalization)
- Retrieval time: < 5ms

### Why BM25 over Vector DB?
| Factor | Vector DB | BM25 |
|---|---|---|
| RAM required | 2GB+ | 50MB |
| Pi Zero 2W support | ❌ | ✅ |
| Retrieval speed | GPU recommended | 5ms CPU |
| Domain accuracy | General semantic | Keyword-specific ✅ |

---

## 📊 Performance Metrics

| Metric | Value |
|---|---|
| Knowledge base | 27,000+ characters |
| Total chunks | 108 semantic chunks |
| BM25 retrieval | < 5ms |
| Google STT latency | ~1 second |
| Groq LLM latency | ~1.2 seconds |
| gTTS generation | ~2 seconds |
| Total response | ~8-10 seconds |
| Hardware cost | ~₹2000 |
| Power consumption | 1.5W |

---



---



---

## 📄 License

This project is licensed under SAD group License.

---

<div align="center">

**Made with ❤️ by SAD Group | CSE IoT CSBT | VIT Pune**

*AURA — Where AI meets Academia*

</div>
