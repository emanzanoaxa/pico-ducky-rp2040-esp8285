# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Pico and Pico W board support


import supervisor


import time
import digitalio
from board import *
import board
from duckyinpython import *
from espatwifi import startWiFi
from espatwebapp import startWebService


# sleep at the start to allow the device to be recognized by the host computer
time.sleep(.5)

# turn off automatically reloading when files are written to the pico
#supervisor.disable_autoreload()
supervisor.runtime.autoreload = False

led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)

progStatus = False
progStatus = getProgrammingStatus()
print("progStatus", progStatus)
if(progStatus == False):
    print("Finding payload")
    # not in setup mode, inject the payload
    payload = selectPayload()
    print("Running ", payload)
    runScript(payload)

    print("Done")
else:
    print("Update your payload")

async def main_loop():
    global led,button1

    print("BOARD ID: ", board.board_id)
    print("Starting Wifi")
    startWiFi()
    print("Starting Web Service")
    webservice_task = asyncio.create_task(startWebService())
    await asyncio.gather(webservice_task)

asyncio.run(main_loop())
