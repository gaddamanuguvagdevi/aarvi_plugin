import gtts
from playsound import playsound
import os

class TTS:
	def __init__(self, lang="en"):
		self.lang = lang

	def play_audio(self, text="Hello world"):
		tts = gtts.gTTS(text, lang=self.lang)

		# save the audio file
		tts.save("text_to_speech.mp3")

		# play the audio file
		playsound("text_to_speech.mp3")
		print('TTS::play_audio ')

	def bg_audio(self):
		# play the audio file
		AARVIFILE = os.path.dirname(os.path.expanduser(__file__))
		playsound(AARVIFILE + "/bgm-final.mp3")
		print('TTS::bg_audio ')

"""
tts = TTS()
tts.play_audio()
tts.bg_audio()
"""
