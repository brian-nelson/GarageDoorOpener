#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import RPi.GPIO as GPIO
from time import sleep
import logging
import logging.handlers
import sys

#constants
PORT_NUMBER = 8080
LOG_FILENAME = "/tmp/GarageDoorOpener.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
SERVICE_FOLDER = "/home/pi/GarageDoorOpener/Server/"


#This class will handles any incoming request from
#the browser
class myHandler(BaseHTTPRequestHandler):
    #Function to return a file to requester
    def send_Response(self, file, mimetype):
        #Open the static file requested and send it
        f = open(SERVICE_FOLDER + file)
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()
        self.wfile.write(f.read())
        f.close()

    #Handler for the GET requests
    def do_GET(self):
        if self.path=="/":
            self.path = "/home.html"

        try:
            #Check the file extension required and
            #set the right mime type

            sendReply = False
            if self.path.endswith(".html"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True

            if sendReply == True:
                self.send_Response(self.path, mimetype)

            return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    #Handler for the POST requests
    def do_POST(self):
        if self.path=="/":
            #pin = 26
            #GPIO.setmode(GPIO.BOARD)

            try:
                #GPIO.setup(pin, GPIO.OUT)
                #GPIO.output(pin, GPIO.HIGH)
                sleep(2)
                #GPIO.output(pin, GPIO.LOW)

                self.send_Response("success.html", "text/html")
            finally:
                #GPIO.cleanup()
                sleep(.1)

        return

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
    def __init__(self, logger, level):
        """Needs a logger and a logger level."""
        self.logger = logger
        self.level = level

    def write(self, message):
        # Only log if there is a message (not just a new line)
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())

try:
    # Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
    # Give the logger a unique name (good practice)
    logger = logging.getLogger(__name__)
    # Set the log level to LOG_LEVEL
    logger.setLevel(LOG_LEVEL)
    # Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
    handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
    # Format each log message like this
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    # Attach the formatter to the handler
    handler.setFormatter(formatter)
    # Attach the handler to the logger
    logger.addHandler(handler)

    # Replace stdout with logging to file at INFO level
    sys.stdout = MyLogger(logger, logging.INFO)

    # Replace stderr with logging to file at ERROR level
    sys.stderr = MyLogger(logger, logging.ERROR)

    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ' , PORT_NUMBER

    #Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()
