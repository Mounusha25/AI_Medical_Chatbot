import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from dotenv import load_dotenv
import os
from groq import Groq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Note: Browser-based live recording via Gradio - no PyAudio needed!
# Gradio handles microphone access through the browser's Web Audio API

def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Note: This function is not used in Hugging Face Spaces.
    Live recording is handled by Gradio's browser-based microphone interface.
    """
    logging.info("Live recording handled by Gradio's browser interface")
    return None

# Setup speech to text - STT model for transcription
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

stt_model = "whisper-large-v3"

def transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY):
    """Transcribe audio file using GROQ Whisper model"""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
        
        return transcription.text
    except Exception as e:
        logging.error(f"Transcription error: {e}")
        return "Unable to process audio. Please try again."

def get_audio_text(audio_file_path):
    """
    Main function to get text from audio file
    Works with:
    - Live recordings from Gradio's microphone interface  
    - Uploaded audio files
    - Compatible with Hugging Face Spaces
    """
    try:
        if audio_file_path is None:
            return "No audio recorded. Please click the record button and speak into your microphone."
        
        # Check if file exists and has content
        if not os.path.exists(audio_file_path):
            return "Audio file not found. Please try recording again."
        
        if os.path.getsize(audio_file_path) == 0:
            return "Empty audio file. Please record again and speak clearly."
        
        # Get GROQ API key
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            return "Audio transcription service not available. Please type your symptoms instead."
        
        # Transcribe the audio using GROQ Whisper
        text = transcribe_with_groq("whisper-large-v3", audio_file_path, groq_api_key)
        
        if text and text.strip():
            logging.info(f"Transcription successful: {text[:50]}...")
            return text
        else:
            return "Unable to transcribe audio. Please speak clearly and try recording again."
            
    except Exception as e:
        logging.error(f"Audio processing error: {e}")
        return "Error processing audio. Please try recording again or type your symptoms."
