from pygame import mixer
import time
class Voice_feedback(object):
    def __init__(self):
        pass
    def voice_play(self,voice):
        mixer.init()
        mixer.music.load(voice)
        mixer.music.play()
        time.sleep(5)
        mixer.music.stop()