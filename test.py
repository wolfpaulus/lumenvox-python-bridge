from array import array
import sys
import lv
mp3=array('c',lv.tts("Hello World"))
mp3.tofile(sys.stdout)
