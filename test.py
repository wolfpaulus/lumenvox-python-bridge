from array import array
import sys
import lv
mp3=array('c',lv.tts("Hello World","am")) # Flags to modify default output format and voice-gender [a]law and [m]
mp3.tofile(sys.stdout)
