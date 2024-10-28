# elevenlabs_tts.py

import os
from io import BytesIO
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def text_to_speech(text: str, voice_id: str = "pNInz6obpgDQGcFmaJgB") -> BytesIO:
    voice_settings = VoiceSettings(
        stability=0.3,          # Doğal ses için uygun ayarlar
        similarity_boost=1.0,
        style=0.2,
        use_speaker_boost=True
    )

    voice = client.text_to_speech.convert(
        voice_id=voice_id,
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=voice_settings
    )

    audio_stream = BytesIO()

    for chunk in voice:
        if chunk:
            audio_stream.write(chunk)

    audio_stream.seek(0)
    return audio_stream