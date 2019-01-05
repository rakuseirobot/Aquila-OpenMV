# RTC Example
#
# This example shows how to use the RTC.
import time
from pyb import RTC

rtc = RTC()
rtc.datetime((2000, 0, 0, 0, 0, 0, 0, 0))

while (True):
    print(rtc.datetime()[5]*60+rtc.datetime()[6])
    time.sleep(1000)
