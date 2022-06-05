import network
from web import Web
from switch import Door, Light
from machine import Pin, I2C
import ssd1306


i2c = I2C(sda=Pin(4), scl=Pin(5))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
display.text('starting...', 0, 0, 1)
display.show()


def do_connect(essid, password):
    import network 
    wifi = network.WLAN(network.STA_IF)  
    if not wifi.isconnected(): 
        print('connecting to network...')
        wifi.active(True) 
        wifi.connect(essid, password) 
        while not wifi.isconnected():
            pass 
    print('network config:', wifi.ifconfig())
    display.fill(0)
    display.text(wifi.ifconfig()[0], 0, 0, 1)
    display.show()
    
do_connect('', '')

CDoor = Door()
CLight = Light()

web = Web()

def Light_func(req):
    if req.url == '/Light_on':
        CLight.on()
    if req.url == '/Light_off':
        CLight.off()
    if req.url == '/Light_status':
        req.response(str(CLight.status))
        return
    req.response('OK')
    
def Door_func(req):
    if req.url == '/Door_open':
        CDoor.up()
    if req.url == '/Door_stop':
        CDoor.stop()
    if req.url == '/Door_close':
        CDoor.down()
    if req.url == '/Door_status':
        req.response(CDoor.status)
        return
    req.response('OK')

def Dete_func(req):
    req.response('NONE')
    
web.apply({
    '/Light_on':Light_func,
    '/Light_off':Light_func,
    '/Light_status':Light_func,
    '/Door_open':Door_func,
    '/Door_stop':Door_func,
    '/Door_close':Door_func,
    '/Door_status':Door_func,
    '/Dete_status':Dete_func,
})

web.active()























