from pygame import mixer
import time

mixer.init()
alert = mixer.Sound('beep.wav')
alert.play()
time.sleep(5)
mixer.quit()
