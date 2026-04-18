import speech_recognition as sr

# Create recognizer once
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300      # sensitivity
recognizer.pause_threshold = 0.8       # seconds of silence = end of sentence
recognizer.dynamic_energy_threshold = True

def listen() -> str:
    """
    Listens via microphone and returns recognised text.
    Uses Google Speech API — very accurate for Indian English.
    Needs internet connection.
    """
    with sr.Microphone() as source:
        print("\n🎤 Adjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🎤 Listening... speak now")

        try:
            # Wait max 8 seconds for speech to start
            # Then max 10 seconds for the full sentence
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
            print("🔄 Processing...")

            # Use Google Speech Recognition
            text = recognizer.recognize_google(audio, language="en-IN")
            text = text.lower().strip()
            print(f"🧑 You said: '{text}'")
            return text

        except sr.WaitTimeoutError:
            print("⏰ No speech detected. Try again.")
            return ""

        except sr.UnknownValueError:
            print("❓ Could not understand. Please speak clearly.")
            return ""

        except sr.RequestError:
            print("🌐 No internet connection. Please check your network.")
            return ""

if __name__ == "__main__":
    print("=" * 40)
    print("  Microphone Test — Google STT")
    print("  Press Ctrl+C to stop")
    print("=" * 40)

    while True:
        try:
            heard = listen()
            if heard:
                print(f"✅ Recognised: {heard}")
                print("-" * 40)
        except KeyboardInterrupt:
            print("\nStopped.")
            break