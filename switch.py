from machine import Pin
import time

TABLE = {
    'up'   :15,
    'down' :26,
    'stop' :19,
    'light':13,
}

class Door:
    def __init__(self):
        self.pup = Pin(TABLE['up'], Pin.OUT, value=1)
        self.pdown = Pin(TABLE['down'], Pin.OUT, value=1)
        self.pstop = Pin(TABLE['stop'], Pin.OUT, value=1)
        self.status = 'stop'
    
    def up(self):
        self.stop()
        self.pup.off()
        self.status = 'up'
    
    def down(self):
        self.stop()
        self.pdown.off()
        self.status = 'down'
    
    def stop(self):
        self.pstop.off()
        time.sleep_ms(100)
        self.pup.on()
        self.pdown.on()
        self.pstop.on()
        self.status = 'stop'

class Light:
    def __init__(self):
        self.pin = Pin(TABLE['light'], Pin.OUT)
        self.status = False
        self.off()
    
    def off(self):
        self.pin.on()
        self.status = False
    
    def on(self):
        self.pin.off()
        self.status = True