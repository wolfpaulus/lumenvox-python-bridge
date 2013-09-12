LumenVox in a Box
Deploying and Interfacing the LumenVox Text-To-Speech Engine on Amazon EC2

Author	
Wolf Paulus
wolf@wolfpaulus.com

Summary
This document describes how to launch an Amazon EC2 RedHat 6.x instance and subsequently deploy and configure a LumenVox Text-to-Speech (TTS) engine on that Linux server instance.
In addition, the implementation of a C-based Python-module is introduced, allowing Python programs access to the TTS engine. This module also converts the LumenVox PCM/Wave voice sound files into the more commonly used MPEG-3 encoding.
Finally, a Python web framework and asynchronous networking library is used to provide Web access to the Text-to-Speech engine, for instance via a remote Web browser.
