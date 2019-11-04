from flask import Flask
import json

app = Flask(__name__)

confFile = "/var/www/html/window.conf"

# Returns a JSON of the window settings.
def getWindowSettings():
    f = open(confFile, "r")
    settings = json.loads(f.read())
    f.close()
    return settings


@app.route("/hello")
def hello():
    return "Hello World!"


# get the data from config file to show brightness level
@app.route("/windowData")
def windowData():
    settings = getWindowSettings()
    return settings


# change the state of the window (aka brightness/on/off)
# This should be a patch method, takes int from 0 to 100
@app.route("/windowBrightness")
def windowBrightness():
    settings = getWindowSettings()
    settings["brightness"] = #new brightness
    '''
    if updateAuto = true:
        updateAuto()
    '''


# update settings file

# flip the autoState
# This should be a put method
@app.route("/updateAuto")
def updateAuto():
    # Grab data
    settings = getWindowSettings()
    # flip auto
    settings["auto"] = 1 - settings["auto"]


if __name__ == "__main__":
    app.run()
