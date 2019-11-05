from flask import Flask, request

"""
TODO: add a method that will instatiate the gpio connection to light
Change the hz
Then disconnect
"""
import json

app = Flask(__name__)

confFile = "/var/www/html/window.conf"

# Returns a JSON of the window settings.
def getWindowSettings():
    f = open(confFile, "r")
    settings = json.loads(f.read())
    f.close()
    return settings


# Updates the window settings
def setWindowSettings(settings):
    f = open(confFile, "w")
    f.write(json.dumps(settings))
    f.close()


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
    data = request.json
    settings["brightness"] = data["brightness"]
    # validation
    if settings["brightness"] > 100:
        settings["brightness"] = 100
    elif settings["brightness"] < 0:
        settings["brightness"] = 0
    setWindowSettings(settings)


# flip the autoState
# This should be a put method
@app.route("/updateAuto", methods=["POST"])
def updateAuto():
    settings = getWindowSettings()
    settings["auto"] = 1 - settings["auto"]
    setWindowSettings(settings)


if __name__ == "__main__":
    app.run()
