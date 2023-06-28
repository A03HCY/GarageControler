from network import WLAN
from network import STA_IF
from time import time
from time import sleep_ms
from gc import mem_free

import lib.datasets as ds

conf = ds.get('wifi')
oled = ds.get('oled')

def connect():
    print("\nAvailable memory: %s Byte" % str(mem_free()))
    wlan = WLAN(STA_IF)
    wlan.active(True)
    start_time = time()
    if oled:
        oled.text("Connect to WiFi",0,16)
        oled.show()
    
    if not wlan.isconnected():
        print("\nThe current device is not networked and is connecting ....")
        wlan.connect(conf['ssid'], conf['password'])
        while not wlan.isconnected():
            sleep_ms(500)
            if time() - start_time > 10:
                print("\nFail !!!")
                break

    if wlan.isconnected():
        IP_info = wlan.ifconfig()
        print("Wifi is connected with the following information:")
        print(" IP address : " + IP_info[0])
        print("Subnet mask : " + IP_info[1])
        print("    Gateway : " + IP_info[2])
        print("        DNS : " + IP_info[3])
        if oled:
            oled.text(": " + IP_info[0],0,32)
            oled.show()
    
    ds.set('wlan', wlan)
    sleep_ms(500)

def isconnected() -> bool:
    if not 'wlan' in ds.keys(): return False
    wlan = ds.get('wlan')
    return wlan.isconnected()