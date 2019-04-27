# Template Matching Example - Normalized Cross Correlation (NCC)
#
# This example shows off how to use the NCC feature of your OpenMV Cam to match
# image patches to parts of an image... expect for extremely controlled enviorments
# NCC is not all to useful.
#
# WARNING: NCC supports needs to be reworked! As of right now this feature needs
# a lot of work to be made into somethin useful. This script will reamin to show
# that the functionality exists, but, in its current state is inadequate.


# OpenMV Cam Master Out Slave In (P0) - Arduino Uno MOSI (11)
# OpenMV Cam Master In Slave Out (P1) - Arduino Uno MISO (12)
# OpenMV Cam Serial Clock        (P2) - Arduino Uno SCK  (13)
# OpenMV Cam Slave Select        (P3) - Arduino Uno SS   (10)
# OpenMV Cam Ground                   - Arduino Ground

import time, sensor, image
from image import SEARCH_EX, SEARCH_DS
import pyb, ustruct

from pyb import LED



red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)
ir_led    = LED(4)

# Reset sensor
sensor.reset()

# Set sensor settings
sensor.set_contrast(1)
sensor.set_gainceiling(16)
# Max resolution for template matching with SEARCH_EX is QQVGA
sensor.set_framesize(sensor.QQVGA)
"""
sensor.QQCIF: 88x72
sensor.QCIF: 176x144
sensor.CIF: 352x288
sensor.QQSIF: 88x60
sensor.QSIF: 176x120
sensor.SIF: 352x240
sensor.QQQQVGA: 40x30
sensor.QQQVGA: 80x60
sensor.QQVGA: 160x120
sensor.QVGA: 320x240
sensor.VGA: 640x480
sensor.HQQQVGA: 80x40
sensor.HQQVGA: 160x80
sensor.HQVGA: 240x160
sensor.B64X32: 64x32 (for use with image.find_displacement())
sensor.B64X64: 64x64 (for use with image.find_displacement())
sensor.B128X64: 128x64 (for use with image.find_displacement())
sensor.B128X128: 128x128 (for use with image.find_displacement())
sensor.LCD: 128x160 (for use with the lcd shield)
sensor.QQVGA2: 128x160 (for use with the lcd shield)
sensor.WVGA: 720x480 (for the MT9V034)
sensor.WVGA2:752x480 (for the MT9V034)
sensor.SVGA: 800x600 (only in JPEG mode for the OV2640 sensor)
sensor.SXGA: 1280x1024 (only in JPEG mode for the OV2640 sensor)
sensor.UXGA: 1600x1200 (only in JPEG mode for the OV2640 sensor)
"""
# You can set windowing to reduce the search image.
#sensor.set_windowing(((640-80)//2, (480-60)//2, 80, 60))
sensor.set_pixformat(sensor.RGB565)

# Load template.
# Template should be a small (eg. 32x32 pixels) grayscale image.
ht = image.Image("/H-UE.pgm")
st = image.Image("/S-UE.pgm")
ut = image.Image("/U-UE.pgm")

brick=False

clock = time.clock()
r=100
g=100
b=100

# Run template matching
while (True):
    clock.tick()
    red_led.on()
    green_led.on()
    blue_led.on()
    ir_led.on()
    img = sensor.snapshot()
    red_led.off()
    green_led.off()
    for blob in img.find_blobs([(33, 56, 30, 78, -128, 85)], pixels_threshold=200, area_threshold=200):
        img.draw_rectangle(blob.rect(),color = (r, g, b))
        img.draw_cross(blob.cx(), blob.cy(),color = (r, g, b))
        print("Lenga!!")
        brick=True
    img.to_grayscale()
    img.binary([(114, 255)])

    # find_template(template, threshold, [roi, step, search])
    # ROI: The region of interest tuple (x, y, w, h).
    # Step: The loop step used (y+=step, x+=step) use a bigger step to make it faster.
    # Search is either image.SEARCH_EX for exhaustive search or image.SEARCH_DS for diamond search
    #
    # Note1: ROI has to be smaller than the image and bigger than the template.
    # Note2: In diamond search, step and ROI are both ignored.

    #h = img.find_template(ht, 0.55, step=5, search=SEARCH_EX) #, roi=(10, 0, 60, 60))
    s = img.find_template(st, 0.435, step=5, search=SEARCH_EX) #1/6の朝時点で0.45,電車内で保存済
    u = img.find_template(ut, 0.45, step=5, search=SEARCH_EX)
    #if h:
    #    img.draw_rectangle(h,color = (r, g, b))
    #    print("h")
    if s:
        img.draw_rectangle(s,color = (r, g, b))
        print("s")
    if u:
        img.draw_rectangle(u,color = (r, g, b))
        print("u")


    print(clock.fps())
