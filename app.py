import numpy as np
import wave
import whisper
import openai
import IPython.display as ipd
import sys
import os
import vosk
import json
import sounddevice as sd
import queue

# Load Whisper model
from IPython.core.display_functions import display

model = whisper.load_model("base")

# OpenAI API key (from environment variable)
key = os.getenv("OPENAI_API_KEY")

if not key:
    raise ValueError("❌ OPENAI_API_KEY environment variable is missing!")


def detect_wake_word_vosk():
    """Uses Vosk to detect 'Hey' wake word."""

    model_path = os.path.join(os.path.dirname(__file__), "vosk-model-small-en-us-0.15")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"❌ Vosk model not found at {model_path}. Download from: https://alphacephei.com/vosk/models")

    # Load Vosk Model
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, 16000)

    q = queue.Queue()

    def callback(indata, frames, time, status):
        """Reads audio from stream into queue."""
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    print("🎤 Listening for 'Hey'...")

    with sd.InputStream(samplerate=16000, channels=1, dtype="int16", callback=callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                print(f"📝 Detected Speech: {text}")

                if "hey" in text:
                    print("✅ 'Doula' detected!")
                    return True


def record_audio_live(filename="user_input.wav", samplerate=44100, duration=10):
    """Records audio after wake word detection."""
    if detect_wake_word_vosk():
        print(f"✅ 'Hey Doula' detected! Recording for {duration} seconds...")

    print("🎤 Recording ongoing...")
    recorded_audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()

    with wave.open(filename, 'wb') as wavefile:
        wavefile.setnchannels(1)
        wavefile.setsampwidth(2)
        wavefile.setframerate(samplerate)
        wavefile.writeframes(recorded_audio.tobytes())

    print(f"✅ Recording saved as {filename}")
    return filename


def speech_to_text(audio_path):
    """Transcribes speech using Whisper."""
    absolute_path = os.path.abspath(audio_path)

    if not os.path.exists(absolute_path):
        raise FileNotFoundError(f"❌ Audio file not found at: {absolute_path}")

    print(f"🔍 Transcribing file from: {absolute_path}")
    result = model.transcribe(absolute_path)
    print(f"📝 Transcription: {result['text']}")

    return result["text"]


def get_ai_response(user_text, key, heart_rate=90, stress_level=5, contractions=3):
    """Generates AI response based on user input and vitals."""
    client = openai.OpenAI(api_key=key)

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
         "content": f"My heart rate is {heart_rate} BPM, my stress level is {stress_level}/10, and I have {contractions} contractions per 10 minutes. Also, {user_text}."}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=100  # Limits response length (~30 sec speech)
        )

        ai_text = response.choices[0].message.content
        print(f"🤖 AI Response: {ai_text}")

        return ai_text

    except openai.AuthenticationError:
        print("❌ API Authentication failed. Check your API key.")
    except openai.RateLimitError:
        print("❌ Rate limit exceeded. Try again later.")
    except openai.APIConnectionError:
        print("❌ Connection error. Check your internet connection.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def text_to_speech(text, output_file="response.mp3"):
    """Converts AI-generated text into speech and plays it."""
    client = openai.OpenAI(api_key=key)

    response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=text,
    )

    with open(output_file, "wb") as f:
        f.write(response.content)

    print(f"🔊 AI Speech saved as {output_file}")
    display(ipd.Audio(output_file, autoplay=True))

def play_relaxing_music(music_file="relaxing_music.mp3"):
    """Plays relaxing background music."""
    if os.path.exists(music_file):
        print(f"🎶 Playing relaxing music: {music_file}")
        display(ipd.Audio(music_file, autoplay=True))
    else:
        print("❌ Relaxing music file not found!")


def live_doula():
    """Runs the full pipeline: listen, record, transcribe, respond, and speak."""
    print("🎬 Starting Doula AI process...")

    audio_file = record_audio_live()
    print("📂 Recorded file:", audio_file)

    transcribed_text = speech_to_text(audio_file).lower()  # Convert to lowercase
    print("📝 Transcription completed:", transcribed_text)

    # 🔹 Check if the user wants relaxing music
    if "relax music" in transcribed_text or "i want some relax music" in transcribed_text:
        print("🎶 Playing relaxing music instead of AI response...")
        play_relaxing_music()  # Play music
        return  # Skip AI response

    # 🤖 Continue AI conversation if no music is requested
    ai_response = get_ai_response(transcribed_text, key, heart_rate=130, stress_level=9, contractions=5)
    print("✅ AI Response received.")

    text_to_speech(ai_response)
    print("🔊 AI Response spoken.")


# Start the Doula system
live_doula()