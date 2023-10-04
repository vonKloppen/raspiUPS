#!/usr/bin/env python3
# Battery control service, send battery state to openHAB, see below and openHAB folder

import requests
import smbus
import time
import syslog
import os

statusCurr = "unknown"
statusPrev = "unknown"
checkInterval = 30
lowTreshold = 40
logIdent = "raspiUPS"
openHaburl = "http://localhost:8080"

def ohSendCommand(item, value):
    # Send Data to openHAB using http post request, good for numbers and switches, but not for contacts
    url = openHaburl+"/rest/items/"+item 
    data = value #str(value)
    requests.post(url, data=data)

def ohUpdateState(item,value):
    # Send Data to openHAB using http put request, good  for contacts
    url = openHaburl+"/rest/items/"+item+"/state"
    requests.put(url, data=value)

## COMMUNICATION SETUP

_REG_CONFIG                 = 0x00
_REG_BUSVOLTAGE             = 0x02
_REG_POWER                  = 0x03
_REG_CURRENT                = 0x04
_REG_CALIBRATION            = 0x05

class BusVoltageRange:
    RANGE_16V               = 0x00

class Gain:
    DIV_2_80MV              = 0x01

class ADCResolution:
    ADCRES_12BIT_32S        = 0x0D

class Mode:
    SANDBVOLT_CONTINUOUS    = 0x07

class INA219:
    def __init__(self, i2c_bus=1, addr=0x40):
        self.bus = smbus.SMBus(i2c_bus);
        self.addr = addr

        self._cal_value = 0
        self._current_lsb = 0
        self._power_lsb = 0
        self.set_calibration_16V_5A()

    def read(self,address):
        data = self.bus.read_i2c_block_data(self.addr, address, 2)
        return ((data[0] * 256 ) + data[1])

    def write(self,address,data):
        temp = [0,0]
        temp[1] = data & 0xFF
        temp[0] =(data & 0xFF00) >> 8
        self.bus.write_i2c_block_data(self.addr,address,temp)

    def set_calibration_16V_5A(self):

        self._current_lsb = 0.1524
        self._cal_value = 26868
        self._power_lsb = 0.003048
        self.write(_REG_CALIBRATION,self._cal_value)
        self.bus_voltage_range = BusVoltageRange.RANGE_16V
        self.gain = Gain.DIV_2_80MV
        self.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.mode = Mode.SANDBVOLT_CONTINUOUS
        self.config = self.bus_voltage_range << 13 | \
                      self.gain << 11 | \
                      self.bus_adc_resolution << 7 | \
                      self.shunt_adc_resolution << 3 | \
                      self.mode
        self.write(_REG_CONFIG,self.config)

    def getBusVoltage_V(self):
        self.write(_REG_CALIBRATION,self._cal_value)
        self.read(_REG_BUSVOLTAGE)
        return (self.read(_REG_BUSVOLTAGE) >> 3) * 0.004

    def getCurrent_mA(self):
        value = self.read(_REG_CURRENT)
        if value > 32767:
            value -= 65535
        return value * self._current_lsb

    def getPower_W(self):
        self.write(_REG_CALIBRATION,self._cal_value)
        value = self.read(_REG_POWER)
        if value > 32767:
            value -= 65535
        return value * self._power_lsb

###

def printToLog(message):

    syslog.openlog(logIdent)
    syslog.syslog(syslog.LOG_INFO, message)
    syslog.closelog()

def checkBattery(percentage):

    if percentage <= lowTreshold:

        printToLog("Battery percentage treshold (%.2f%%) reached, shutting down.." %lowTreshold)
        ohUpdateState("MwBatteryShutdown","CLOSED")
        os.system("poweroff")

    else:

        printToLog("Battery remaining: %.2f" %percentage)



if __name__=='__main__':

    ina219 = INA219(i2c_bus=10,addr=0x43)
    # Initialize
    ohUpdateState("MwBatteryShutdown","OPEN")


    while True:

        currentTime = time.strftime("%H:%M:%S", time.localtime())
        currentDate = time.strftime("%Y-%m-%d", time.localtime())

        try:

            bus_voltage = ina219.getBusVoltage_V()
            ohSendCommand("MwBatteryVoltage",str(bus_voltage))

        except:

            printToLog("Error (E1)")

        try:

            current = ina219.getCurrent_mA()
            ohSendCommand("MwBatteryCurrent",str(current))

        except:

            printToLog("Error (E2)")

        try:

            power = ina219.getPower_W()
            ohSendCommand("MwBatteryPower",str(power))

        except:

            printToLog("Error (E3)")

        try:

            battPercentage = (bus_voltage - 3)/1.2*100

        except:

            printToLog("Error (E4)")


        if(battPercentage > 100):

            battPercentage = 100

        if(battPercentage < 0):

            battPercentage = 0

        # send after corrections
        ohSendCommand("MwBatterySoC",str(battPercentage))

        if current >= 0:

            statusCurr = "on mains"

            if statusCurr != statusPrev:

                printToLog("Status changed: " + statusCurr)
                ohUpdateState("MwBatteryUse","OPEN")

            statusPrev = "on mains"

        else:

            statusCurr = "on battery"

            if statusCurr != statusPrev:

                printToLog("Status changed: " + statusCurr)
                ohUpdateState("MwBatteryUse","CLOSED")

            statusPrev = "on battery"
            checkBattery(battPercentage)

        
        time.sleep(checkInterval)

    syslog.closelog()






