# SPI with the Arduino as the master device and the OpenMV Cam as the slave.
#
# Please wire up your OpenMV Cam to your Arduino like this:
#
# OpenMV Cam Master Out Slave In (P0) - Arduino Uno MOSI (11)
# OpenMV Cam Master In Slave Out (P1) - Arduino Uno MISO (12)
# OpenMV Cam Serial Clock        (P2) - Arduino Uno SCK  (13)
# OpenMV Cam Slave Select        (P3) - Arduino Uno SS   (10)
# OpenMV Cam Ground                   - Arduino Ground



"""
H:2    -- Sig:1
S:1    -- Sig:2
U:0    -- Sig:3
"""

import time, sensor, image
from image import SEARCH_EX, SEARCH_DS
import pyb, ustruct
from pyb import LED

from machine import I2C

# Reset sensor
sensor.reset()

# Set sensor settings
sensor.set_contrast(1)
sensor.set_gainceiling(16)
# Max resolution for template matching with SEARCH_EX is QQVGA
sensor.set_framesize(sensor.QQVGA)
# You can set windowing to reduce the search image.
#sensor.set_windowing(((640-80)//2, (480-60)//2, 80, 60))
sensor.set_pixformat(sensor.GRAYSCALE)
spi = pyb.SPI(2, pyb.SPI.SLAVE)
spi.init(2,pyb.SPI.SLAVE, polarity = 0, phase = 0, bits = 8)
sig = pyb.Pin("P3", pyb.Pin.OUT_PP,pyb.Pin.PULL_DOWN)
pin = pyb.Pin("P9", pyb.Pin.IN, pull=pyb.Pin.PULL_UP)
ht = image.Image("/H.pgm")
st = image.Image("/S.pgm")
ut = image.Image("/U.pgm")

ddr=0xB4
dr=bytearray([0xB4])
data = bytearray(3)

i2c = I2C(scl="P4",sda="P5",freq=120000)

led = pyb.Pin("P8", pyb.Pin.OUT_PP,pyb.Pin.PULL_NONE)

red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)
ir_led    = LED(4)

for a in range(10):
    red_led.on()
    green_led.off()
    blue_led.off()
    time.sleep(50)
    red_led.off()
    green_led.on()
    blue_led.off()
    time.sleep(50)
    red_led.off()
    green_led.off()
    blue_led.on()
    time.sleep(50)
red_led.off()
green_led.off()
blue_led.off()
led.value(0)
couaaat=0
bb=b'\x00'
def callback(line):
    print(pin.value())
    led.value(1)
    if pin.value()==1:
        allow = False
    else:
        allow = True
    led.value(0)
    print(allow)

#ss = pyb.ExtInt(pin, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_UP, callback)

clock = time.clock()

# Note that for sync up to work correctly the OpenMV Cam must be running this script before the
# Arduino starts to poll the OpenMV Cam for data. Otherwise the SPI byte framing gets messed up,
# and etc. So, keep the Arduino in reset until the OpenMV Cam is "Waiting for Arduino...".
aaa=int(0)
print(aaa)
res={"h":False,"s":False,"u":False}
allow=False
Trans=False
#ss.enable()
while(True):
    if allow:
        print("allow!!")
        red_led.off()
        blue_led.on()
        clock.tick()
        img = sensor.snapshot()

        # find_template(template, threshold, [roi, step, search])
        # ROI: The region of interest tuple (x, y, w, h).
        # Step: The loop step used (y+=step, x+=step) use a bigger step to make it faster.
        # Search is either image.SEARCH_EX for exhaustive search or image.SEARCH_DS for diamond search
        #
        # Note1: ROI has to be smaller than the image and bigger than the template.
        # Note2: In diamond search, step and ROI are both ignored.
        h = img.find_template(ht, 0.58, step=8, search=SEARCH_EX) #, roi=(10, 0, 60, 60))
        s = img.find_template(st, 0.5, step=8, search=SEARCH_EX)
        u = img.find_template(ut, 0.56, step=8, search=SEARCH_EX)
        if (h or s or u):
            blue_led.on()
            green_led.on()
            Trans=True
            allow=False
        if h:
            img.draw_rectangle(h)
            #print("h")
            res["h"]=True
        if s:
            img.draw_rectangle(s)
            #print("s")
            res["s"]=True
        if u:
            img.draw_rectangle(u)
            #print("u")
            res["u"]=True

        if Trans:
            blue_led.off()
            #print("reback")
            aaa=0
            if res["u"] and not (res["s"] or res["h"]):
                aaa=5
            elif res["s"] and not (res["u"] or res["h"]):
                aaa=4
            elif res["h"] and not (res["s"] or res["u"]):
                aaa=3
            elif not (res["h"] or res["s"] or res["u"]):
                aaa=8
            else:
                aaa=7
            #ss.disable()
            sig.value(0)
            while(pin.value()==0): pass
            while(pin.value()==1): pass
            try:
                spi.send(aaa)
            except:
                green_led.off()
            res["u"]=False
            res["s"]=False
            res["h"]=False
            Trans=False
            allow=False
            # If we failed to sync up the first time we'll sync up the next time.
            #print(bbb) # Only reached on no error.
            while(pin.value()==0): pass
            sig.value(1)
            while(pin.value()==1): pass
            #ss.enable()
            sig.value(1)
            green_led.off()

            print(pin.value())
            time.sleep(5)

        blue_led.off()


    if pin.value()==1:
        allow = False
    else:
        allow = True
    print(pin.value())

    if not (allow):
        sig.value(1)
        print("wait")
        #ss.enable()
        red_led.on()
        #print("wait\r")
