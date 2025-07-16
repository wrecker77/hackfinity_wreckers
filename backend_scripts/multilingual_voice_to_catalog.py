import os
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import requests
import threading
import time
from deep_translator import GoogleTranslator
from cohere_product_pipeline import process_user_input

# Your AssemblyAI API key here
ASSEMBLYAI_API_KEY = "b6e4bad374774de0934049a037d79e2b"
HEADERS = {"authorization": ASSEMBLYAI_API_KEY}
UPLOAD_ENDPOINT = "https://api.assemblyai.com/v2/upload"
TRANSCRIBE_ENDPOINT = "https://api.assemblyai.com/v2/transcript"

def record_audio():
    print("\n🎙️ Speak now... Press Enter to stop recording.\n")
    stop_flag = threading.Event()

    def wait_for_enter():
        input()
        stop_flag.set()

    threading.Thread(target=wait_for_enter, daemon=True).start()

    samplerate = 16000
    audio_buffer = []

    def callback(indata, frames, time_info, status):
        if stop_flag.is_set():
            raise sd.CallbackStop()
        audio_buffer.append(indata.copy())

    try:
        with sd.InputStream(samplerate=samplerate, channels=1, callback=callback):
            while not stop_flag.is_set():
                sd.sleep(100)
    except sd.CallbackStop:
        pass

    if not audio_buffer:
        print("❌ No audio captured. Please try again.")
        return None

    audio = np.concatenate(audio_buffer, axis=0)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav.write(tmp_file.name, samplerate, (audio * 32767).astype(np.int16))
    return tmp_file.name

def upload_to_assemblyai(audio_path):
    with open(audio_path, "rb") as f:
        response = requests.post(UPLOAD_ENDPOINT, headers=HEADERS, data=f)
    response.raise_for_status()
    return response.json()["upload_url"]

def transcribe_audio(audio_url):
    payload = {
        "audio_url": audio_url,
        "language_detection": True,
    }
    response = requests.post(TRANSCRIBE_ENDPOINT, headers=HEADERS, json=payload)
    response.raise_for_status()
    transcript_id = response.json()["id"]

    print("🧠 Transcribing...")

    while True:
        poll_response = requests.get(f"{TRANSCRIBE_ENDPOINT}/{transcript_id}", headers=HEADERS)
        poll_response.raise_for_status()
        status = poll_response.json()["status"]

        if status == "completed":
            return poll_response.json()["text"]
        elif status == "error":
            raise RuntimeError(f"Transcription error: {poll_response.json().get('error')}")
        time.sleep(2)

def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        return text  # Return original as fallback

def main():
    try:
        audio_path = record_audio()
        if not audio_path:
            return

        upload_url = upload_to_assemblyai(audio_path)
        transcribed_text = transcribe_audio(upload_url)
        print(f"\n📝 Detected Language Text:\n{transcribed_text}\n")

        translated_text = translate_to_english(transcribed_text)
        print(f"🌐 Translated to English:\n{translated_text}\n")

        results = process_user_input(translated_text)
        print("📦 Product Descriptions:\n")
        for item in results:
            print(item["description"])
            print("-" * 40)

    except Exception as e:
        print(f"\n❌ Critical error: {e}")
    finally:
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception:
            pass

if __name__ == "__main__":
    main()
