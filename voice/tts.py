import pyttsx3

_engine = pyttsx3.init()
_engine.setProperty('rate', 155)      # speaking speed
_engine.setProperty('volume', 1.0)    # full volume

# Pick a clear voice
voices = _engine.getProperty('voices')
for voice in voices:
    if "zira" in voice.name.lower() or "female" in voice.name.lower():
        _engine.setProperty('voice', voice.id)
        break

def speak(text: str):
    """Make DISHA speak out loud"""
    print(f"🤖 DISHA : {text}")
    _engine.say(text)
    _engine.runAndWait()

if __name__ == "__main__":
    speak("Hello! I am DISHA, your department assistant. How can I help you today?")