# I2C Control
#
# This example shows how to use the i2c bus on your OpenMV Cam by dumping the
# contents on a standard EEPROM. To run this example either connect the
# Thermopile Shield to your OpenMV Cam or an I2C EEPROM to your OpenMV Cam.

from machine import I2C
import pyb

ddr=0xB4
dr=bytearray([0xB4])
data = bytearray(3)

i2c = I2C(scl="P4",sda="P5",freq=120000)
#print(i2c.scan())
#while(True):
#    pass

while(True):
    #print(i2c.scan())
    i2c.start()
    try:
        i2c.writeto(ddr>>1,bytearray([0x07]),False)
        #i2c.start()
        data=i2c.readfrom(ddr>>1,3)
        temp=(data[1]<<8)+data[0]
        #print(i2c.scan())
        i2c.start()
        i2c.writeto(ddr>>1,bytearray([0x06]),False)
        #i2c.start()
        data=i2c.readfrom(ddr>>1,3)
        temp2=(data[1]<<8)+data[0]
        print(str(temp)+","+str(temp2)+","+str(temp-temp2))
        data = bytearray(3)
        temp=0
        temp2=0
    except:
        pass
