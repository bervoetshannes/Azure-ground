# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
import uuid
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
import config
import random
import time
import datetime
import json
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

pin_to_circuit = 7

def rc_time (pin_to_circuit):
    count = 0
  
    #Output on the pin for 
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(20)

    #Change the pin back to input
    GPIO.setup(pin_to_circuit, GPIO.IN)
  
    #Count until the pin goes high
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1

    return count

#Catch when script is interrupted, cleanup correctly
try:
    # Main loop
    while True:
        time.sleep(10)
        print(rc_time(pin_to_circuit))
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()

async def main():
    # get connection string from config.py (not stored in git)
    conn_str = config.connstr

    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the client.
    await device_client.connect()

    async def send_message(temperature, light):
        print("sending message with temperature " + str(temperature))
        print("sending message with temperature " + str(light))

        body = {
            "time": str(datetime.datetime.utcnow()),
            "light": light,
            "temperature": temperature,
            "deviceId": "myDevice"
        }

        

        msg = Message(json.dumps(body))

        # message-id is a user-settable identifier for the message
        msg.message_id = uuid.uuid4()

        # custom_properties is a dictionary of application properaties
        if temperature > 25:
            msg.custom_properties["alert"] = "too hot"
            print("we sent an alert")

        if light > 10:
            msg.custom_properties["alert"] = "too dark"
            print("sent an alarm")

        # json format
        msg.content_encoding = "UTF-8"
        msg.content_type = "application/json"

        # send the message and wait until sent
        await device_client.send_message(msg)
        print("done sending message")

    # send `messages_to_send` messages in parallel
    while True:
        light = rc_time()
        temperature = 20 + random.random() * 10
        await send_message(temperature)
        await send_message(light)
        time.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())

    # If using Python 3.6 or below, use the following code instead of asyncio.run(main()):
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(main())
    #loop.close()