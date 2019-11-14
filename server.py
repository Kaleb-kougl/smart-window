from flask import Flask, request, Response
from datetime import datetime
import RPi.GPIO as GPIO
import json, time, logging, logging.config, yaml
logging.config.dictConfig(yaml.load(open('logging.conf')))

logfile    = logging.getLogger('file')
logconsole = logging.getLogger('console')
logfile.debug("Debug FILE")
logconsole.debug("Debug CONSOLE")

# THIS IS AN HTTP SERVER

GPIO.setmode(GPIO.BCM)
pin = 21
GPIO.setup(12, GPIO.OUT)

app = Flask(__name__)

confFile = "/var/www/html/window.conf"
errorFile = "/var/www/html/errorsReport.txt"

# Returns a JSON of the window settings.
def getWindowSettings():
    # add try except blocks
    try:
        f = open(confFile, "r")
        settings = json.loads(f.read())
    except IOError as error:
        print(error)
        fe = open(errorFile, "w")
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        fe.write(error + timestamp)
        fe.close()
    finally:
        f.close()
        return settings


# Updates the window settings
def setWindowSettings(settings):
    # add try except blocks
    try:
        f = open(confFile, "w")
        f.write(json.dumps(settings))
    except IOError as error:
        print(error)
        fe = open(errorFile, "w")
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        fe.write(error + timestamp)
        fe.close()
    finally:
        f.close()


def updatePhysicalWindow(previous, settings):
    # pin, frequency
    pi = GPIO.PWM(pin, 0)
    # duty cycle
    pi.start(previous)
    time.sleep(0.1)
    pi.ChangeDutyCycle(settings["brightness"])


@app.route("/hello")
def hello():
    return "Hello, it me. Smart window."


# get the data from config file to show brightness level
@app.route("/windowData")
def windowData():
    settings = getWindowSettings()
    return settings


# change the state of the window (aka brightness/on/off)
# int from 0 to 100
@app.route("/windowBrightness", methods=["PUT"])
def windowBrightness():
    settings = getWindowSettings()
    if settings["auto"]:
        previousBrightness = settings["brightness"]
        data = request.json
        settings["brightness"] = data["brightness"]
        # validation
        if settings["brightness"] > 100:
            settings["brightness"] = 100
        elif settings["brightness"] < 0:
            settings["brightness"] = 0
        setWindowSettings(settings)
        updatePhysicalWindow(previousBrightness, settings)
    else:
        resp = Response(
            {"error": "Conflicts with current state of server"},
            status=409,
            mimetype="application/json",
        )
        return resp


# flip the autoState
# This should be a put method
@app.route("/updateAuto", methods=["POST"])
def updateAuto():
    settings = getWindowSettings()
    settings["auto"] = 1 - settings["auto"]
    setWindowSettings(settings)


if __name__ == "__main__":
    app.run()
