import io
from gtts import gTTS, gTTSError

class AudioService:
    @staticmethod
    def create_audio(text: str, lang: str = 'nl') -> io.BytesIO:
        try:
            tts = gTTS(text, lang=lang, slow=True)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf
        except (gTTSError, ConnectionError, Exception) as e:
            raise Exception(f"Audio creation failed: {e}")