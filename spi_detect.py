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
from pyb import RTC

rtc = RTC()
rtc.datetime((2000, 0, 0, 0, 0, 0, 0, 0))

sensor.reset()
sensor.set_contrast(1)
sensor.set_gainceiling(16)
sensor.set_framesize(sensor.QQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)
spi = pyb.SPI(2, pyb.SPI.SLAVE)
spi.init(2,pyb.SPI.SLAVE, polarity = 0, phase = 0, bits = 8)
sig = pyb.Pin("P3", pyb.Pin.OUT_PP,pyb.Pin.PULL_DOWN)
pin = pyb.Pin("P9", pyb.Pin.IN, pull=pyb.Pin.PULL_UP)
ht = image.Image("/H.pgm")
st = image.Image("/S.pgm")
ut = image.Image("/U.pgm")
i2c = I2C(scl="P4",sda="P5",freq=120000)
led = pyb.Pin("P8", pyb.Pin.OUT_PP,pyb.Pin.PULL_NONE)
clock = time.clock()
aaa=int(0)
print(aaa)
res={"h":False,"s":False,"u":False,"sermo":False}
allow=False
Trans=False
sermo_thre=50  #温度用閾値
timout=4 #xmega timeout
timflag=True

ddr=0xB4
dr=bytearray([0xB4])
data = bytearray(3)
couaaat=0
bb=b'\x00'
red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)
ir_led    = LED(4)

def sermo_check():
    i2c.start()
    i2c.writeto(ddr>>1,bytearray([0x07]),False)
    data=i2c.readfrom(ddr>>1,3)
    temp=(data[1]<<8)+data[0]
    i2c.start()
    i2c.writeto(ddr>>1,bytearray([0x06]),False)
    data=i2c.readfrom(ddr>>1,3)
    temp2=(data[1]<<8)+data[0]
    print(temp-temp2)
    data = bytearray(3)
    if temp-temp2>=sermo_thre:
        return True
    else:
        return False


for a in range(7):#Waiting for waking up xmega
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
slflag=False


while(True):
    try:
        if pin.value()==1:
            allow = False
        else:
            allow = True
        #print(pin.value())
        if allow:
            #print("allow!!")
            red_led.off()
            blue_led.on()
            clock.tick()
            img = sensor.snapshot()
            img.binary([(114, 255)])
            h = img.find_template(ht, 0.55, step=8, search=SEARCH_EX) #, roi=(10, 0, 60, 60))
            s = img.find_template(st, 0.43, step=8, search=SEARCH_EX) #1/6の朝時点で0.45,電車内で保存済
            u = img.find_template(ut, 0.56, step=8, search=SEARCH_EX)
            sermo = sermo_check()
            if (h or s or u or sermo):
                blue_led.on()
                green_led.on()
                Trans=True
                allow=False
                slflag=True
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
            if sermo:
                res["sermo"]=True
            if Trans:
                blue_led.off()
                #print("reback")
                aaa=0
                if res["u"] and not (res["s"] or res["h"] or res["sermo"]):
                    aaa=5
                elif res["s"] and not (res["u"] or res["h"] or res["sermo"]):
                    aaa=4
                elif res["h"] and not (res["s"] or res["u"] or res["sermo"]):
                    aaa=3
                elif res["sermo"] and not (res["s"] or res["h"] or res["u"]):
                    aaa=6
                elif not (res["h"] or res["s"] or res["u"]):
                    aaa=8
                else:
                    aaa=7
                #ss.disable()
                sig.value(0)

                first=rtc.datetime()[5]*60+rtc.datetime()[6]
                while(pin.value()==0):
                    if ((rtc.datetime()[5]*60+rtc.datetime()[6]-first)>timout):
                        timflag=False
                        break
                if timflag:
                    while(pin.value()==1):
                        if ((rtc.datetime()[5]*60+rtc.datetime()[6]-first)>timout):
                            timflag=False
                            break
                if timflag:
                    try:
                        spi.send(aaa,timeout=3000)
                        first=rtc.datetime()[5]*60+rtc.datetime()[6]
                        while(pin.value()==0):
                            if ((rtc.datetime()[5]*60+rtc.datetime()[6]-first)>timout):
                                break
                        sig.value(1)
                        if timflag:
                            while(pin.value()==1):
                                if ((rtc.datetime()[5]*60+rtc.datetime()[6]-first)>timout):
                                    break
                    except:
                        green_led.off()

                timflag=False
                sig.value(1)
                green_led.off()
                res["u"]=False
                res["s"]=False
                res["h"]=False
                res["sermo"]=False
                Trans=False
                allow=False
                #print(pin.value())
                time.sleep(100)
                if slflag or timflag:
                    time.sleep(2000)
            slfkag=False
            timflag=True
            blue_led.off()

        else:
            sig.value(1)
            #print("wait")
            red_led.on()
    except:
        pass
