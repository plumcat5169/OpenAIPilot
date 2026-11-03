"""
Voice command recognizer scaffold using SpeechRecognition and PyAudio.
"""

# Attempt to import SpeechRecognition; if unavailable (or its dependencies fail),
# expose a safe stub that raises an informative error when used.
try:
    import speech_recognition as sr
except Exception as e:
    sr = None
    from ..logger import logger
    logger.warning(f"SpeechRecognition (or its dependencies) could not be imported: {e}")

from ..logger import logger

class VoiceRecognizer:
    def __init__(self):
        if sr is None:
            raise RuntimeError("SpeechRecognition is not available; voice commands cannot be used.")
        # Microphone initialization may fail if pyaudio is missing; handle gracefully.
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize microphone (pyaudio may be missing): {e}")

    def listen(self, timeout: float | None = None, phrase_time_limit: float | None = None) -> str | None:
        """Capture audio from the default microphone and return transcribed text.
        Returns ``None`` if speech could not be recognized or on request errors.
        """
        if sr is None:
            logger.error("Attempted to use VoiceRecognizer, but SpeechRecognition is unavailable.")
            return None
        try:
            with self.microphone as source:
                logger.info("Adjusting for ambient noise – please wait...")
                self.recognizer.adjust_for_ambient_noise(source)
                logger.info("Listening for voice input...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except Exception as e:
            logger.error(f"Error accessing microphone or listening: {e}")
            return None
        try:
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized speech: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("Speech was unintelligible.")
            return None
        except sr.RequestError as e:
            logger.error(f"SpeechRecognition request failed: {e}")
            return None
    def listen(self, timeout: float | None = None, phrase_time_limit: float | None = None) -> str | None:
        """Capture audio from the default microphone and return transcribed text.
        Returns ``None`` if speech could not be recognized or on request errors.
        """
        with self.microphone as source:
            logger.info("Adjusting for ambient noise – please wait...")
            self.recognizer.adjust_for_ambient_noise(source)
            logger.info("Listening for voice input...")
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        try:
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized speech: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("Speech was unintelligible.")
            return None
        except sr.RequestError as e:
            logger.error(f"SpeechRecognition request failed: {e}")
            return None
