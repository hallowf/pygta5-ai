import time, os, sys, threading, logging
from flask import Flask, request, jsonify
from flask_api import status
import flask
import numpy as np

from utils import Cabinet

app = Flask(__name__)

file_monitor = Cabinet()


@app.route("/gta-api-watcher-<string:identifier>", methods=["GET", "POST"])
def start_watcher(identifier):
    if not file_monitor.is_running or not file_monitor.values_registered:
        counter = getattr(request.args, "counter", 0)
        split_at = getattr(request.args, "split", 2000)
        file_monitor.register_values(identifier,counter,split_at)
        file_monitor.thread_watcher()
        print("Started watcher")
        return "ok", status.HTTP_200_OK
    else:
        print("Watcher is running")
        return "watcher running", status.HTTP_503_SERVICE_UNAVAILABLE


@app.route("/gta-api", methods=["POST"])
def receive_data():
    content = request.json
    file_monitor.received_data.append([np.array(content["screen"]), content["output"]])
    return "ok", status.HTTP_200_OK

# For testing purposes also requires time to be sent in json
@app.route("/gta-api-test", methods=["POST"])
def receive_data_test():
    content = request.json
    received_data.append([np.array(content["screen"]), content["output"]])
    now = time.time()
    return "{}".format(now-content["time"]), status.HTTP_200_OK

def silence_logger():
    logFormatStr = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    logging.basicConfig(format = logFormatStr, filename = "global.log", level=logging.DEBUG)
    formatter = logging.Formatter(logFormatStr,'%m-%d %H:%M:%S')
    fileHandler = logging.FileHandler("summary.log")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)
    app.logger.addHandler(fileHandler)
    app.logger.addHandler(streamHandler)
    app.logger.info("Logging is set up.")

if __name__ == '__main__':
    silence_logger()
    socketio.run(app.run(host= '0.0.0.0',port=int("2890"),debug=False))
