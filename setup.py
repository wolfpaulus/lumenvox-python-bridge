from distutils.core import setup, Extension

module1 = Extension('lvmodule',
sources = ['lvmodule.c'],
library_dirs=['/usr/lib64'], 
libraries=['lv_lvspeechport','mp3lame','python2.6'],
include_dirs=['/usr/include'])

setup(name='lvmodule', 
version='1.0', 
description = 'Python Interface for LumenVox TTS',
ext_modules=[module1])
