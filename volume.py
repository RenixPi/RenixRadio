import smbus2
import websocket
import json
import time
import RPi.GPIO as GPIO
from time import sleep
import i2cEncoderLibV2
from colour import Color
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

try:
    from systemd import journal
except ImportError:
    pass
else:
    logger.addHandler(journal.JournaldLogHandler())

global isconnected
global websocket

isconnected = False
ws  = None

blue = Color("blue")
red = Color("red")
blue_red = list(blue.range_to(red, 101))

def on_message(ws, message):
    logger.debug(message)

def on_error(ws, error):
    logger.error(error)

def on_close(ws, close_status_code, close_msg):
    logger.info("### closed ###")
    isconnected = False

def on_open(ws):
    ws = ws
    logger.info("### open ###")
    isconnected = True
    logger.info("connected? {}".format(isconnected))

def set_volume(value):
    if not ws:
       logger.info("socket not available")
       return

    ws.send(json.dumps({"volume": value}))

#def ws_connect():
#    # websocket.enableTrace(True)
#    websocket.WebSocketApp("ws://127.0.0.1:54545/state",
#                              on_open=on_open,
#                              on_message=on_message,
#                              on_error=on_error,
#                              on_close=on_close)
    #ws.run_forever()



def EncoderChange():
    value = round(encoder.readCounter32())
    color = blue_red[value]
    encoder.writeLEDG(round(color.green * 100))
    encoder.writeLEDB(round(color.blue * 100))
    encoder.writeLEDR(round(color.red * 100))

    set_volume(value)

    #encoder.writeRGBCode(blue_red[value].hex)

    #encoder.writeLEDG(100)
    logger.debug('Changed: %d' % (encoder.readCounter32()))
    #encoder.writeLEDG(0)

def EncoderPush():
#    encoder.writeLEDB(100)
    logger.debug('Encoder Pushed!')
#    encoder.writeLEDB(0)

def EncoderDoublePush():
#    encoder.writeLEDB(100)
#    encoder.writeLEDG(100)
    logger.debug('Encoder Double Push!')
#    encoder.writeLEDB(0)
#    encoder.writeLEDG(0)

def EncoderMax():
#    encoder.writeLEDR(100)
    logger.debug('Encoder max!')
#    encoder.writeLEDR(0)

def EncoderMin():
#    encoder.writeLEDR(100)
    logger.debug('Encoder min!')
#    encoder.writeLEDR(0)

def Encoder_INT():
    encoder.updateStatus()
#    GPIO.remove_event_detect(INT_pin)
#    GPIO.add_event_detect(INT_pin, GPIO.FALLING, callback=lambda x=ws: Encoder_INT(x), bouncetime=10)

GPIO.setmode(GPIO.BCM)
bus = smbus2.SMBus(1)
INT_pin = 4
GPIO.setup(INT_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

encoder = i2cEncoderLibV2.i2cEncoderLibV2(bus, 0x1c)

encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_DISABLE | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
encoder.begin(encconfig)

encoder.writeCounter(0)
encoder.writeMax(100)
encoder.writeMin(0)
encoder.writeStep(3)
encoder.writeAntibouncingPeriod(8)
encoder.writeDoublePushPeriod(50)
encoder.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
encoder.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)
encoder.writeRGBCode(0xcc00cc)


encoder.onChange = EncoderChange
encoder.onButtonPush = EncoderPush
encoder.onButtonDoublePush = EncoderDoublePush
encoder.onMax = EncoderMax
encoder.onMin = EncoderMin

encoder.autoconfigInterrupt()
print ('Board ID code: 0x%X' % (encoder.readIDCode()))
print ('Board Version: 0x%X' % (encoder.readVersion()))

encoder.writeRGBCode(0x640000)
sleep(0.3)
encoder.writeRGBCode(0x006400)
sleep(0.3)
encoder.writeRGBCode(0x000064)
sleep(0.3)
encoder.writeRGBCode(0x00)

GPIO.add_event_detect(INT_pin, GPIO.FALLING, callback=lambda x=ws: Encoder_INT(x), bouncetime=10)

ws = websocket.WebSocketApp("ws://127.0.0.1:54545/state",
                              on_open=on_open,
#                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

logger.info("running forever")
ws.run_forever()

logger.info("no longer running")

#while True:
#  if GPIO.input(INT_pin) == False: #
#    Encoder_INT() #
#    pass
