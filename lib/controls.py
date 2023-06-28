import lib.datasets as ds
import time
from machine import Pin

ds.setdict({
    'door' : 'stop',
    'light': 'off' ,
    'pins' : {
        'up':21,
        'dw':19,
        'sp':18,
        'lt': 5,
    },
    'linspace':0,
    'temptime':0
})

def pin_out(key:str) -> Pin:
    pio = ds.get('pins').get(key, 0)
    return Pin(pio, Pin.OUT, value=0)

class Door:
    def __init__(self) -> None:
        self.pup   = pin_out('up')
        self.pdown = pin_out('dw')
        self.pstop = pin_out('sp')
        self.status('stop')
    
    @property
    def info(self):
        return ds.get('door')
    
    @property
    def height(self):
        return ds.get('linspace') / 8
    
    def status(self, value):
        ds.set('door', value)
    
    def fixtime(self):
        if ds.get('linspace') < 0:
            ds.set('linspace', 0)
    
    def up(self):
        self.stop()
        self.pup.on()
        self.status('up')
        ds.set('temptime', time.time())
    
    def down(self):
        self.stop()
        self.pdown.on()
        self.status('down')
        ds.set('temptime', time.time())
    
    def stop(self):
        self.pup.off()
        self.pdown.off()
        self.pstop.on()
        time.sleep_ms(100)
        self.pstop.off()
        if ds.get('door') == 'up':
            ds.set('linspace', ds.get('linspace') + time.time() - ds.get('temptime'))
        if ds.get('door') == 'down':
            ds.set('linspace', ds.get('linspace') - time.time() + ds.get('temptime'))
        self.status('stop')
        ds.set('temptime', 0)
        self.fixtime()
    
    def approach(self, apnum:int):
        self.stop()
        now = ds.get('linspace')
        if now > apnum:
            self.down()
            time.sleep(now - apnum)
            self.stop()
        elif now == apnum:
            return
        else:
            self.up()
            time.sleep(apnum - now)
            self.stop()


class Light:
    def __init__(self) -> None:
        self.pin = pin_out('lt')
    
    @property
    def info(self):
        return ds.get('light')
    
    def status(self, value) -> str:
        ds.set('light', value)
    
    def off(self):
        self.pin.off()
        self.status('off')
    
    def on(self):
        self.pin.on()
        self.status('on')