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

