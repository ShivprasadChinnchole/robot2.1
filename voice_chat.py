import os
import sys
import subprocess
import threading
import time
import queue
import pyaudio
import speech_recognition as sr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain.query_handler import get_answer
from colorama import Fore, Style, init

init(autoreset=True)

# ── Global state ──────────────────────────────────────────────
stop_speaking   = False
current_process = None
is_speaking     = False
interrupt_queue = queue.Queue()
audio_queue     = queue.Queue()

# ── Audio config ──────────────────────────────────────────────
CHUNK    = 1024
RATE     = 16000
CHANNELS = 1

# ── Permanent mic stream ──────────────────────────────────────
def audio_capture_loop():
    """One permanent mic stream — never closes, no conflicts"""
    pa = pyaudio.PyAudio()

    device_index = None
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0 and 'microphone' in info['name'].lower():
            device_index = i
            break

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK
    )

    print(Fore.CYAN + "   Permanent mic stream started")

    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_queue.put(data)
        except Exception:
            time.sleep(0.01)

def get_audio_chunk(seconds: float) -> bytes:
    """Collect audio chunks for given number of seconds"""
    chunks = []
    needed = int((RATE / CHUNK) * seconds)

    # Clear stale audio
    while not audio_queue.empty():
        audio_queue.get()

    for _ in range(needed):
        try:
            chunk = audio_queue.get(timeout=2)
            chunks.append(chunk)
        except queue.Empty:
            break
    return b''.join(chunks)

def recognize(audio_bytes: bytes) -> str:
    """Convert raw audio bytes to text"""
    rec = sr.Recognizer()
    try:
        audio = sr.AudioData(audio_bytes, RATE, 2)
        return rec.recognize_google(audio, language="en-IN").lower().strip()
    except Exception:
        return ""

# ── Interrupt detection ───────────────────────────────────────
def interrupt_detection_loop():
    """
    Always running in background.
    When DISHA is speaking — listens for any interrupt phrase.
    Uses same permanent mic stream — no conflict.
    """
    # All phrases that mean STOP
    interrupt_phrases = [
        "disha stop",
        "stop disha",
        "disha",
        "stop",
        "enough",
        "quiet",
        "shut up",
        "pause",
        "wait"
    ]

    while True:
        if not is_speaking:
            time.sleep(0.1)
            continue

        # Grab 1 second of audio — fast response
        audio_bytes = get_audio_chunk(1.0)
        if not audio_bytes:
            continue

        text = recognize(audio_bytes)
        if text:
            print(Fore.YELLOW + f"\n   [Interrupt heard: '{text}']")
            if any(phrase in text for phrase in interrupt_phrases):
                print(Fore.YELLOW + "   [STOP detected!]")
                interrupt_queue.put("stop")

# ── TTS ───────────────────────────────────────────────────────
def stop_speech():
    global stop_speaking, current_process, is_speaking
    stop_speaking = True
    is_speaking   = False
    if current_process:
        try:
            current_process.terminate()
            current_process = None
        except Exception:
            pass

def speak(text: str):
    """
    Speaks sentence by sentence.
    Stops instantly when interrupt_queue receives a signal.
    """
    global stop_speaking, current_process, is_speaking
    stop_speaking = False
    is_speaking   = True

    # Clear old interrupts
    while not interrupt_queue.empty():
        interrupt_queue.get()

    clean = (text
             .replace("'", "")
             .replace('"',  '')
             .replace('\n', ' ')
             .replace('%',  'percent')
             .replace('&',  'and'))

    sentences = [s.strip() for s in clean.split('.') if s.strip()]

    for sentence in sentences:
        if stop_speaking or not interrupt_queue.empty():
            break

        current_process = subprocess.Popen([
            'powershell', '-NoProfile', '-WindowStyle', 'Hidden',
            '-Command',
            f"Add-Type -AssemblyName System.Speech; "
            f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.Rate = 1; $s.Volume = 100; "
            f"$s.Speak('{sentence}');"
        ])

        # Check for interrupt every 50ms while sentence plays
        while current_process.poll() is None:
            if stop_speaking or not interrupt_queue.empty():
                stop_speech()
                break
            time.sleep(0.05)

    is_speaking = False

# ── Main STT ──────────────────────────────────────────────────
def listen() -> str:
    """Listen for user question — uses permanent mic stream"""
    print(Fore.CYAN + "\n🎤 Listening... speak now")

    # Clear stale audio before listening
    while not audio_queue.empty():
        audio_queue.get()

    # Collect 6 seconds and recognise
    audio_bytes = get_audio_chunk(6.0)
    text = recognize(audio_bytes)

    if text:
        print(Fore.CYAN + f"   Recognised: '{text}'")
    return text

# ── UI Helpers ────────────────────────────────────────────────
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(Fore.CYAN + "=" * 60)
    print(Fore.CYAN + "   DISHA — Department Intelligent Smart Helper")
    print(Fore.CYAN + "   Speak your question after the mic prompt")
    print(Fore.CYAN + "   Say 'Disha stop' anytime to interrupt")
    print(Fore.CYAN + "   Say 'bye' to exit")
    print(Fore.CYAN + "=" * 60)
    print()

def disha_print(text):
    print(Fore.GREEN + "🤖 DISHA : " + Style.RESET_ALL + text)

def user_print(text):
    print(Fore.YELLOW + f"🧑 You    : {text}")

def speak_and_wait(text: str):
    """Speak and block until done — for short responses"""
    t = threading.Thread(target=speak, args=(text,), daemon=True)
    t.start()
    t.join()

# ── Main Loop ─────────────────────────────────────────────────
def run():
    clear_screen()
    print_banner()

    # Start permanent mic capture
    mic_thread = threading.Thread(target=audio_capture_loop, daemon=True)
    mic_thread.start()
    time.sleep(1)

    # Start interrupt detection
    int_thread = threading.Thread(target=interrupt_detection_loop, daemon=True)
    int_thread.start()

    # Greeting
    greeting = ("Hello! I am DISHA your Department Intelligent Smart Helper. "
                "You can ask me about classrooms, faculty, "
                "announcements, and department information. "
                "Say Disha stop anytime to interrupt me. "
                "Say bye to exit.")
    disha_print(greeting)
    speak_and_wait(greeting)

    while True:
        try:
            print(Fore.CYAN + "\n" + "-" * 60)

            # ── STEP 1: Listen for question ───────────────────
            user_input = listen()

            if not user_input:
                msg = "I did not catch that. Please speak again."
                disha_print(msg)
                speak_and_wait(msg)
                continue

            user_print(user_input)

            # ── STEP 2: Exit check ────────────────────────────
            if any(w in user_input for w in ["bye", "exit", "quit", "goodbye"]):
                farewell = "Goodbye! Have a wonderful day. See you soon!"
                disha_print(farewell)
                speak_and_wait(farewell)
                break

            # ── STEP 3: Think ─────────────────────────────────
            print(Fore.CYAN + "🔄 Thinking...")
            answer = get_answer(user_input)
            disha_print(answer)

            # ── STEP 4: Speak answer in background ───────────
            speak_thread = threading.Thread(
                target=speak, args=(answer,), daemon=True
            )
            speak_thread.start()

            # ── STEP 5: Wait — stop only on interrupt ─────────
            while speak_thread.is_alive():
                if not interrupt_queue.empty():
                    interrupt_queue.get()
                    stop_speech()
                    time.sleep(0.3)
                    msg = "Okay. What would you like to ask?"
                    disha_print(msg)
                    speak_and_wait(msg)
                    break
                time.sleep(0.05)

        except KeyboardInterrupt:
            stop_speech()
            farewell = "Goodbye! Have a great day!"
            disha_print(farewell)
            speak_and_wait(farewell)
            break

        except Exception as e:
            stop_speech()
            print(Fore.RED + f"[ERROR] {e}")
            msg = "Sorry, something went wrong. Please try again."
            disha_print(msg)
            speak_and_wait(msg)

if __name__ == "__main__":
    run()