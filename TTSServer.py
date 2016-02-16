#!/usr/bin/python
#
# TTS Server utilizing LumenVox-Python-Bridge
# Copyright 2013. All rights reserved.
# Author: Wolf Paulus, wolf@wolfpaulus.com
#
#from __future__ import unicode_literals

import subprocess
import tempfile
import os.path
from array import array

import tornado.httpserver
import tornado.ioloop
import tornado.web
#import lv


class TTSHandler(tornado.web.RequestHandler):
    def get(self):
        inp = str(self.get_argument("text", default=[], strip=True))
        flags = str(self.get_argument("flags", default=None, strip=True))
        mp3 = array('c', str(lv.tts(inp, flags)))
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
        wav = array('c', str(lv.tts(TTSHandlerALAW.ssml1 + inp + TTSHandlerALAW.ssml2, flags + "a")))
        self.set_header("Content-Type", "audio/x-wav")
        self.set_header("Content-Length", len(wav))
        self.write(wav.tostring())


class StaticHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('./static/index.html')


class OTSHandler(tornado.web.RequestHandler):
    def post(self):
        ratio = int(self.get_argument("ratio", default="20", strip=True)) # 1..100
        format = str(self.get_argument("format", default="text", strip=True)) # text|html
        content = self.get_argument("text", default=[], strip=True)

        if format.lower() == "html":
            format = "-h"
        else:
            format = ""

        if 0<ratio and ratio<=100:
            ratio = "-r " + str(ratio)
        else:
            ratio = "-a"
            format = ""


        try:
            content = content.encode('utf-8')
            content = str(content.decode('ascii', 'ignore'))
        except:
            content= str(content)


        temp_dir = tempfile.mkdtemp() # create temp directory and two temp files
        temp1 = tempfile.NamedTemporaryFile(suffix=".txt", dir=temp_dir, delete=False)
        temp2 = tempfile.NamedTemporaryFile(suffix=".txt", dir=temp_dir, delete=False)

        result = None
        try:
            #
            #   write text content into file to be summarized
            #
            temp1.write(content)
            temp1.close()
            cmdline = '{0} {1} {2} -o {3} {4}'.format('/usr/local/bin/ots', ratio, format, temp2.name, temp1.name)
            #
            #   summarize into temp2
            #
            result = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE).communicate()[0]

        finally:
            # cleanup
            temp1.close()
            os.remove(temp1.name)
            s = temp2.read()
            temp2.close()
            os.remove(temp2.name)
            self.set_header("Content-Type", "text/plain")
            self.write(s)


port = 8000 # 80 or 8000
settings = {"static_path": os.path.join(os.path.dirname(__file__), "static"), }
application = tornado.web.Application([(r"/", IndexHandler),
                                       (r"/lvtts", TTSHandler),
                                       (r"/alaw", TTSHandlerALAW),
                                       (r"/ots", OTSHandler),
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