from machine import Pin, PWM
import utime
from time import sleep

MAX_PWM = 65025

redPwm = PWM(Pin(26))
redPwm.freq(1000)
greenPwm = PWM(Pin(4))
greenPwm.freq(1000)
bluePwm = PWM(Pin(12))
bluePwm.freq(1000)

selectedPercentRed = 1.0
selectedPercentGreen = 1.0
selectedPercentBlue = 1.0
selectedBrightness = 1.0

def cleanPwmValue(pwmValue):
    return max(0, min(round(pwmValue), MAX_PWM))

def isValidPercentValue(percentValue=None):
    if percentValue is not None and percentValue >= 0.0 and percentValue <= 1.0:
        return True
    else:
        return False

def setColor(percentRed=None, percentGreen=None, percentBlue=None, brightness=None):
    global selectedPercentRed
    global selectedPercentGreen
    global selectedPercentBlue
    global selectedBrightness

    if isValidPercentValue(percentRed):
        selectedPercentRed = percentRed
        
    if isValidPercentValue(percentGreen):
        selectedPercentGreen = percentGreen
        
    if isValidPercentValue(percentBlue):
        selectedPercentBlue = percentBlue
        
    if isValidPercentValue(brightness):
        selectedBrightness = brightness
        
    red = cleanPwmValue(MAX_PWM * selectedPercentRed * selectedBrightness)
    green = cleanPwmValue(MAX_PWM * selectedPercentGreen * selectedBrightness)
    blue = cleanPwmValue(MAX_PWM * selectedPercentBlue * selectedBrightness)
    
    redPwm.duty_u16(red)
    greenPwm.duty_u16(green)
    bluePwm.duty_u16(blue)

setColor()

clkPin = Pin(8, Pin.IN)
dtPin = Pin(7, Pin.IN)
btnPin = Pin(6, Pin.IN, Pin.PULL_UP)

clkLastState = clkPin.value()
lastBtnPress = utime.ticks_ms()

settings = ("BRIGHTNESS", "RED", "GREEN", "BLUE")
currentSettingIndex = 0

def getCurrentSetting():
    global settings
    global currentSettingIndex
    return settings[currentSettingIndex]

def getNextSetting():
    global settings
    global currentSettingIndex
    currentSettingIndex += 1
    if currentSettingIndex >= len(settings):
        currentSettingIndex = 0
    return getCurrentSetting()

SETTING_ADJUST = 0.1

def adjustSetting(increase=True):
    global selectedPercentRed
    global selectedPercentGreen
    global selectedPercentBlue
    global selectedBrightness
    
    setting = getCurrentSetting()

    if setting == "RED":
        if increase:
            selectedPercentRed += SETTING_ADJUST
            if not isValidPercentValue(selectedPercentRed):
                selectedPercentRed = 1.0
        else:
            selectedPercentRed -= SETTING_ADJUST
            if not isValidPercentValue(selectedPercentRed):
                selectedPercentRed = 0.0
    if setting == "GREEN":
        if increase:
            selectedPercentGreen += SETTING_ADJUST
            if not isValidPercentValue(selectedPercentGreen):
                selectedPercentGreen = 1.0
        else:
            selectedPercentGreen -= SETTING_ADJUST
            if not isValidPercentValue(selectedPercentGreen):
                selectedPercentGreen = 0.0
    if setting == "BLUE":
        if increase:
            selectedPercentBlue += SETTING_ADJUST
            if not isValidPercentValue(selectedPercentBlue):
                selectedPercentBlue = 1.0
        else:
            selectedPercentBlue -= SETTING_ADJUST
            if not isValidPercentValue(selectedPercentBlue):
                selectedPercentBlue = 0.0
    if setting == "BRIGHTNESS":
        if increase:
            selectedBrightness += SETTING_ADJUST
            if not isValidPercentValue(selectedBrightness):
                selectedBrightness = 1.0
        else:
            selectedBrightness -= SETTING_ADJUST
            if not isValidPercentValue(selectedBrightness):
                selectedBrightness = 0.0
    setColor()


def handleEncoder():
    global clkPin
    global clkCurrentState
    global clkLastState
    global counter
    
    clkCurrentState = clkPin.value()
    dtState = dtPin.value()
    btnState = btnPin.value()
  
    if clkCurrentState != clkLastState and clkCurrentState == 1:
        if dtState != clkCurrentState:
            adjustSetting()
        else:
            adjustSetting(increase=False)
    
    clkLastState = clkCurrentState

clkPin.irq(handler=lambda pin: handleEncoder())

def handleButtonPress():
    global btnPin
    global lastBtnPress

    btnState = btnPin.value()
    now_ms = utime.ticks_ms()
    if btnState == 0:
        if now_ms - lastBtnPress > 300:
            setting = getNextSetting()
            print("new setting", setting)
            if setting == "RED":
                redPwm.duty_u16(MAX_PWM)
                greenPwm.duty_u16(0)
                bluePwm.duty_u16(0)
                sleep(0.2)
                setColor()
            if setting == "GREEN":
                redPwm.duty_u16(0)
                greenPwm.duty_u16(MAX_PWM)
                bluePwm.duty_u16(0)
                sleep(0.2)
                setColor()
            if setting == "BLUE":
                redPwm.duty_u16(0)
                greenPwm.duty_u16(0)
                bluePwm.duty_u16(MAX_PWM)
                sleep(0.2)
                setColor()
            if setting == "BRIGHTNESS":
                redPwm.duty_u16(MAX_PWM)
                greenPwm.duty_u16(MAX_PWM)
                bluePwm.duty_u16(MAX_PWM)
                sleep(0.2)
                setColor()
        lastBtnPress = now_ms
        
btnPin.irq(handler=lambda pin: handleButtonPress())