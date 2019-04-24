from pygame import mixer
mixer.init()
alert = mixer.sound('bell.wav')
alert.play()
alert.close
mixer.close()