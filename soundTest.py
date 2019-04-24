from pygame import mixer
mixer.init()
alert = mixer.sound('beep.wav')
alert.play()
alert.close
mixer.close()