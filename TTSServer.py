#!/usr/bin/python
#
# LumenVox TTS Server Interface
# Copyright 2013. All rights reserved.
# Author: Wolf Paulus, wolf@wolfpaulus.com
#

import tornado.httpserver
import tornado.ioloop
import tornado.web

from array import array
import sys
import lv

class TTSHandler(tornado.web.RequestHandler):
    def get(self):
        inp = str(self.get_argument("text", default=[], strip=True))
        mp3=array('c',lv.tts(inp))
        self.set_header("Content-Type", "audio/mpeg")
        self.write(mp3.tostring())

port = 8000
application = tornado.web.Application([(r"/lvtts", TTSHandler),])


if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    try:
        print "Tornado Server Starting ..."
        tornado.ioloop.IOLoop.instance().start()
    except:
        print "... Tornado Server Stopped"