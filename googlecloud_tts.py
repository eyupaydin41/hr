import os
import requests
from io import BytesIO
from dotenv import load_dotenv
import streamlit as st
import base64

load_dotenv()
API_KEY = os.getenv("GOOGLETTS_API_KEY")

def text_to_speech(text: str, language_code: str = "tr-TR", voice_name: str = "tr-TR-Wavenet-C") -> BytesIO:
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "input": {"text": text},
        "voice": {"languageCode": language_code, "name": voice_name},
        "audioConfig": {"audioEncoding": "MP3"}
    }

    response = requests.post(
        f"https://texttospeech.googleapis.com/v1/text:synthesize?key={API_KEY}",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        raise Exception(f"Google TTS API isteği başarısız oldu: {response.text}")

    audio_content = response.json()["audioContent"]
    audio_data = base64.b64decode(audio_content)
    audio_stream = BytesIO(audio_data)
    audio_stream.seek(0)
    return audio_stream
