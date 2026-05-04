import os
import base64
import tempfile
import logging

from groq import Groq
from gtts import gTTS

logger = logging.getLogger(__name__)


def encode_image_from_bytes(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')


def analyze_image_with_groq(query: str, encoded_image: str, model: str = "meta-llama/llama-4-scout-17b-16e-instruct") -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                },
            ],
        }
    ]
    chat_completion = client.chat.completions.create(messages=messages, model=model)
    return chat_completion.choices[0].message.content


def consult_text_with_groq(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return chat_completion.choices[0].message.content


def transcribe_audio_with_groq(audio_bytes: bytes, model: str = "whisper-large-v3") -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(audio_bytes)
        temp_file_path = temp_file.name

    try:
        with open(temp_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                language="en"
            )
        return transcription.text
    finally:
        os.unlink(temp_file_path)


def text_to_speech_gtts(text: str, language: str = "en") -> bytes | None:
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            tts.save(temp_file.name)
            temp_file_path = temp_file.name
        try:
            with open(temp_file_path, "rb") as audio_file:
                return audio_file.read()
        finally:
            os.unlink(temp_file_path)
    except Exception as e:
        logger.error("Error generating speech: %s", e)
        return None
