# DoulaAI

An AI-powered personalized system designed to reduce anxiety during childbirth by monitoring contractions and providing soothing, real-time responses when medical staff are not present.

---

## Project Description

DoulaAI is a modular system that provides emotional and mental support during labor using artificial intelligence.  
The system includes:

- Wake word detection using Vosk to activate listening.
- Live audio recording following wake word detection.
- Speech-to-text transcription via OpenAI's Whisper model.
- Personalized AI-generated responses based on physiological parameters (heart rate, stress level, contraction frequency) using GPT-4o.
- Text-to-speech conversion to deliver audible calming messages.
- Optional relaxing background music playback.
- A Streamlit-based interactive questionnaire UI to collect user preferences for a tailored experience.

---

## Folder Structure

- `live_doula.py` — Main script that runs the live pipeline: wake word detection, recording, transcription, AI response, and speech playback.
- `app.py` — Streamlit app providing a personalization questionnaire for users.
- `vosk-model-small-en-us-0.15/` — Vosk model folder for wake word recognition (download separately).
- `relaxing_music.mp3` — Sample relaxing music file (optional).
- `requirements.txt` — Python dependencies list.
- `new logo.png` — Logo displayed in the Streamlit questionnaire app.

---

## Installation Requirements

- Python 3.8 or higher
- Install required packages with:  
