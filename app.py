import streamlit as st
import numpy as np
import wave
import whisper
import openai
import os
import vosk
import json
import sounddevice as sd
import queue
import sys
import time

# Load Whisper model
model = whisper.load_model("base")

# OpenAI API key (from environment variable)
key = os.getenv("OPENAI_API_KEY")
if not key:
    st.error("❌ OPENAI_API_KEY environment variable is missing!")
    st.stop()

# Streamlit UI
st.image("logo.jpg", width=200)  # Ensure your logo file is correctly placed
st.title("🍼 Live Doula AI - Birth Assistant")
st.write("A real-time AI assistant to provide *calming support* during childbirth.")

# Ensure session state exists
if "wake_word_detected" not in st.session_state:
    st.session_state.wake_word_detected = False


def detect_wake_word_vosk():
    """Continuously listens for 'Hey Doula' and resets session after response."""
    model_path = "vosk-model-small-en-us-0.15"

    if not os.path.exists(model_path):
        st.error(f"❌ Vosk model not found at {model_path}. Download from: https://alphacephei.com/vosk/models")
        return False

    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, 16000)
    q = queue.Queue()

    def callback(indata, frames, time, status):
        """Reads audio from stream into queue."""
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    while not st.session_state.wake_word_detected:
        st.write("🎤 Listening for 'Hey Doula'...")
        with sd.InputStream(samplerate=16000, channels=1, dtype="int16", callback=callback):
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").lower()

                    if "hey" in text or "hey doula" in text:
                        st.session_state.wake_word_detected = True
                        st.success("✅ 'Hey Doula' detected! Now recording request...")
                        return True


def record_audio_live(filename="user_input.wav", samplerate=44100, duration=10):
    """Records audio for 10 seconds after 'Hey Doula' is detected."""
    if not st.session_state.wake_word_detected:
        return None

    st.write("🎤 Recording request for 10 seconds...")
    recorded_audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()

    with wave.open(filename, 'wb') as wavefile:
        wavefile.setnchannels(1)
        wavefile.setsampwidth(2)
        wavefile.setframerate(samplerate)
        wavefile.writeframes(recorded_audio.tobytes())

    return filename


def speech_to_text(audio_path):
    """Transcribes speech using Whisper."""
    result = model.transcribe(audio_path)
    return result["text"].lower()


def get_ai_response(user_text, heart_rate=90, stress_level=5, contractions=3):
    """Generates AI response or plays relaxing music if requested."""
    client = openai.OpenAI(api_key=key)

    if "relax music" in user_text or "i want some relax music" in user_text or "play relaxing music" in user_text:
        music_file = os.path.abspath("relaxing_music.mp3")

        if os.path.exists(music_file):
            st.success("🎶 Playing relaxing music...")
            st.audio(music_file)
            return None
        else:
            st.error("❌ Relaxing music file not found! Please check the file location.")
            return None

    system_prompt = """
    You are a *calming birth assistant AI* helping a woman in labor.
    You analyze her *heart rate, stress levels, and contractions* to provide personalized *soothing and mindful* responses.

    - Keep responses concise, calming, and clear (~20 sec of speech).
    - If heart rate > 120 or stress level > 8, focus on deep breathing.
    - If contractions are strong, remind her to relax and breathe.
    - If distress is too high, suggest calling the nursing staff.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",
         "content": f"My heart rate is {heart_rate} BPM, stress is {stress_level}/10, and I have {contractions} contractions per 10 min. Also, {user_text}."}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


def text_to_speech(text, output_file="response.mp3"):
    """Converts AI-generated text into speech only if text is valid."""
    if not text or text.strip() == "":
        return

    client = openai.OpenAI(api_key=key)

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text,
        )

        with open(output_file, "wb") as f:
            f.write(response.content)

        st.success("🔊 AI Speech generated!")
        st.audio(output_file)

    except openai.OpenAIError as e:
        st.error(f"❌ Text-to-Speech Error: {e}")


def play_relaxing_music(music_file="relaxing_music.mp3"):
    """Plays relaxing background music."""
    if os.path.exists(music_file):
        st.success("🎶 Playing relaxing music...")
        st.audio(music_file)
    else:
        st.error("❌ Relaxing music file not found!")


# ✅ Main logic: Automatically loops back to listening after each response
while True:
    detect_wake_word_vosk()

    if st.session_state.wake_word_detected:
        audio_file = record_audio_live()

        if audio_file:
            transcribed_text = speech_to_text(audio_file)

            if "relax music" in transcribed_text or "i want some relax music" in transcribed_text:
                play_relaxing_music()
            else:
                ai_response = get_ai_response(transcribed_text, heart_rate=130, stress_level=9, contractions=5)
                text_to_speech(ai_response)

        # ⏳ Wait 5 minutes before resetting the session
        st.session_state.wake_word_detected = False
        st.success("⏳ Waiting 5 minutes before listening again...")
        time.sleep(300)  # 5-minute wait
