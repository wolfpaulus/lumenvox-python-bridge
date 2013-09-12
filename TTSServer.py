#!/usr/bin/python
#
# TTS Server utilizing LumenVox-Python-Bridge
# Copyright 2013. All rights reserved.
# Author: Wolf Paulus, wolf@wolfpaulus.com
#
import tempfile
import os.path
from array import array

import tornado.httpserver
import tornado.ioloop
import tornado.web

import lv


class TTSHandler(tornado.web.RequestHandler):
    def get(self):
        inp = str(self.get_argument("text", default=[], strip=True))
        flags = str(self.get_argument("flags", default=None, strip=True))
        mp3 = array('c', lv.tts(inp, flags))
        self.set_header("Content-Type", "audio/mpeg")
        self.write(mp3.tostring())

    def post(self):
        inp = str(self.get_argument("text", default=[], strip=True))
        flags = str(self.get_argument("flags", default=None, strip=True))
        tf = tempfile.NamedTemporaryFile(mode='w+b', suffix='.mp3', dir='./static/tmp', delete=False)
        tf.write(lv.tts(inp, flags))
        tf.close()
        self.set_header("Content-Type", "text/plain")
        self.write("/static/tmp/" + os.path.basename(tf.name))


class TTSHandlerALAW(tornado.web.RequestHandler):
    ssml1 = """<?xml version="1.0"?>
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.w3.org/2001/10/synthesis
            http://www.w3.org/TR/speech-synthesis/synthesis.xsd" xml:lang="en-US">
            <say-as interpret-as="characters">"""
    ssml2 = "</say-as></speak>"

    def get(self):
        inp = str(self.get_argument("text", default=[], strip=True))
        flags = str(self.get_argument("flags", default=None, strip=True))
        wav = array('c', lv.tts(TTSHandlerALAW.ssml1 + inp + TTSHandlerALAW.ssml2, flags+"a"))
        self.set_header("Content-Type", "audio/x-wav")
        self.set_header("Content-Length", len(wav))
        self.write(wav.tostring())


class StaticHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('./static/index.html')


port = 8000
settings = {"static_path": os.path.join(os.path.dirname(__file__), "static"), }
application = tornado.web.Application([(r"/", IndexHandler),
                                       (r"/lvtts", TTSHandler),
                                       (r"/alaw", TTSHandlerALAW),
                                       (r"/(.*)", StaticHandler, {"path": "./static"}),
                                      ], **settings)

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)

    try:
        print "Tornado Server Starting (v22KHz) ..."
        tornado.ioloop.IOLoop.instance().start()
    except:
        print "... Tornado Server Stopped"