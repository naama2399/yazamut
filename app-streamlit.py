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
import base64

# Load Whisper model
model = whisper.load_model("base")

# OpenAI API key (from environment variable)
key = os.getenv("OPENAI_API_KEY")
if not key:
    st.error("❌ OPENAI_API_KEY environment variable is missing!")
    st.stop()

# Ensure the image file is in the correct directory
logo_path = "logo.jpg"  # Make sure the correct filename is used


def get_image_base64(image_path):
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


if os.path.exists(logo_path):
    image_base64 = get_image_base64(logo_path)
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/jpeg;base64,{image_base64}" width="200">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("⚠ Logo image not found! Please check the file path.")

st.title("🍼 Live Doula AI - Birth Assistant")
st.write("A real-time AI assistant to provide calming support during childbirth.")

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


def record_audio_live(filename="user_input.wav", samplerate=44100, duration=5):
    """Records audio for 5 seconds after 'Hey Doula' is detected."""
    if not st.session_state.wake_word_detected:
        return None

    st.write("🎤 Recording request for 5 seconds...")
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
    You are a calming birth assistant AI designed to provide emotional and mental support during childbirth.

    - Your focus is on *calming techniques, relaxation, and mindfulness*.
    - *Do NOT provide medical advice or diagnose conditions*.
    - *DO NOT mention labor status, medical risks, or suggest medical actions*.
    - *Keep responses concise and within 30 seconds of speech (~100 tokens).*
    - If a user expresses stress, anxiety, or discomfort, respond with *soothing breathing exercises, positive affirmations, and relaxation techniques*.
    - Encourage the user to *focus on deep breaths, softening their body, and maintaining a calm state of mind*.
    - If a user asks medical-related questions (e.g., "Is my baby okay?"), gently *redirect them to a healthcare provider* and reinforce *calmness and reassurance*.
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
            max_tokens=100  # Limits response length (~30 sec speech)
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

            if "relax music" in transcribed_text or "i want some relax music" in transcribed_text or "play relaxing " \
                                                                                                     "music" in \
                    transcribed_text:
                play_relaxing_music()
                # Wait for the music to finish (assuming ~150 seconds)
                time.sleep(160)  # Adjust according to actual music length
            else:
                ai_response = get_ai_response(transcribed_text, heart_rate=130, stress_level=9, contractions=5)
                if ai_response:
                    text_to_speech(ai_response)
                    # Estimate speech duration (~30 seconds max)
                    time.sleep(30)

        # 🔄 Only restart listening after playback finishes
        st.session_state.wake_word_detected = False
