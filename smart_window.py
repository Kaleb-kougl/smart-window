import RPi.GPIO as GPIO
import time, json, requests

# THIS IS A CRON JOB

GPIO.setmode(GPIO.BCM)


#### CONFIGURATION ####
pin = 21
GPIO.setup(pin, GPIO.OUT)

# lat & long for location
lat = 41.94
lon = -87.65

# Darksky API key
api_key = "YOUR_API_KEY"

# Brightness levels (percent)
cloudy = 40
mixed = 60
sunny = 80

# Config file, persistent configs
confFile = "/var/www/html/window.conf"

# Debug, show output
debug = True
#### END OF CONFIGURATION ####


# Load config file for cache/settings
f = open(confFile, "r")
settings = json.loads(f.read())
f.close()

if not int(settings["auto"]):
    if debug:
        print("Auto brightness disabled, exiting...")
    exit()

weatherUrl = (
    "https://api.darksky.net/forecast/" + api_key + "/" + str(lat) + "," + str(lon)
)
weatherUrl = weatherUrl + "?exclude=minutely,hourly,alerts,flags"

# Refresh weather data every 15 minutes
if (settings["timestamp"] + 900) < time.time():
    try:
        if debug:
            print("Getting Darksky weather data...")

        data = requests.get(url, timeout=10).json()

        # Save/cache values
        settings["auto"] = 1
        settings["cloudCover"] = data["currently"]["cloudCover"]
        settings["sunrise"] = data["daily"]["data"][0]["sunriseTime"]
        settings["sunset"] = data["daily"]["data"][0]["sunsetTime"]
        settings["timestamp"] = round(time.time())

        f = open(confFile, "w")
        f.write(json.dumps(settings))
        f.close()

    except:
        print("Error: Unable to connect to Darksky API")

# Set max brightness based on weather
if settings["cloudCover"] > 0.8:
    maxBright = cloudy
elif settings["cloudCover"] < 0.3:
    maxBright = sunny
else:
    maxBright = mixed

if debug:
    print(
        "Cloud cover: "
        + str(settings["cloudCover"])
        + ", Sunrise: "
        + str(settings["sunrise"])
        + ", Sunset: "
        + str(settings["sunset"])
    )
    print("Max brightness: " + str(maxBright))

# Current time
cTime = time.localtime()
now = time.time()

# Sunrise: start brightening 20 mins before, end 70 mins after
sunriseStart = int(settings["sunrise"]) - 1200
sunriseEnd = sunriseStart + 5400

# Sunset: start dimming 75 mins before, end 15 mins after
sunsetStart = int(settings["sunset"]) - 4500
sunsetEnd = sunsetStart + 5400


# Determine the current brightness
if now >= sunriseStart and now <= sunriseEnd:
    elapsed = now - sunriseStart
    percent = elapsed / 5400
    brightness = maxBright * percent
    timeOfDay = "Sunrise"

elif now > sunriseEnd and now < sunsetStart:
    brightness = maxBright
    timeOfDay = "Day"

elif now >= sunsetStart and now <= sunsetEnd:
    elapsed = sunsetEnd - now
    percent = elapsed / 5400
    brightness = maxBright * percent
    timeOfDay = "Sunset"

else:
    brightness = 0
    timeOfDay = "Night"

if debug:
    print(timeOfDay + ", Brightness: " + str(brightness))

# Change the brightness quicker at the beginning of the
# transition, then slowing near the end
def getChangeAmt(current, target):
    return round(abs(current - target) / 10) + 1


# You're going to change the duty cycle to change the intensity of the light.
currentBrightness = 0
# HIT my server and get current brightness...
windowDataUrl = "http://myRaspberryPiServer/windowData"
windowData = requests.get(windowDataUrl, timeout=10).json()


# need some sort of way to still update the physical window
pi = GPIO.PWN(pin, 0)


targetBrightness = brightness

# Brightness increasing
if targetBrightness > currentBrightness:
    while currentBrightness <= targetBrightness:
        pi.ChangeDutyCycle(currentBrightness)

        amt = getChangeAmt(currentBrightness, targetBrightness)

        currentBrightness = currentBrightness + amt
        time.sleep(0.05)

# Brightness decreasing
elif targetBrightness < currentBrightness:
    while currentBrightness >= targetBrightness:
        pi.ChangeDutyCycle(currentBrightness)

        amt = getChangeAmt(currentBrightness, targetBrightness)

        currentBrightness = currentBrightness - amt
        time.sleep(0.05)
