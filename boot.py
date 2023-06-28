import lib.datasets as ds
import os

ds.init()

if 'database' in os.listdir('/'):
    for item in os.listdir('/database'):
        if not '.json' in item: continue
        try: ds.load_json('/database/' + item)
        except: continue


from machine import I2C,Pin
from lib.ssd1306 import SSD1306_I2C

ds.setdefault('oled')
try:
    i2c = I2C(scl = Pin(4),sda = Pin(2),freq = 1000000)
    oled = SSD1306_I2C(128, 64, i2c)
    oled.text("Load Database",0,0)
    oled.show()
    ds.set('oled', oled)
except:
    print('Fail to init oled')