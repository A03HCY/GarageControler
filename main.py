import lib.datasets as ds
import lib.controls as ctl
import lib.wifi     as wifi
import machine , time
from lib.web    import Web , Req


door  = ctl.Door()
light = ctl.Light()

wifi.connect()

# ========== 外部中断
btn = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_UP)
def handle_interrupt(pin):
    time.sleep_ms(500)
    if door.info == 'stop':
        print('自动化关闭')
        door.approach(0)
        light.off()
    else:
        print('紧急制动')
        door.stop()
btn.irq(trigger=machine.Pin.IRQ_FALLING, handler=handle_interrupt)

# ========== 网络 API
try:
    web = Web()
except:
    machine.reset()

def app(req:Req):
    req.response('gcon_v2')
web.route('/app', app)

# 运行状态
def status(req:Req):
    if 'light' in req.url:
        req.response(ds.get('light'))
    if 'door' in req.url:
        req.response(ds.get('door'))
    if 'height' in req.url:
        req.response(str(door.height))
        
web.listrout(status, [
    '/info_light', '/info_door', '/info_height'
])

# 状态控制
def control(req:Req):
    if 'on'  in req.url: light.on()
    if 'off' in req.url: light.off()
    if 'up'   in req.url: door.up()
    if 'down' in req.url: door.down()
    if 'stop' in req.url: door.stop()
    req.response('OK')

web.listrout(control, [
    '/api/light_on', '/api/light_off', '/api/door_up', '/api/door_down', '/api/door_stop'
])

# 自动模式
def approach(req:Req):
    if 'open' in req.url:
        req.response('OK')
        light.on()
        door.approach(ds.get('Auto_height', 32))
        return
    if 'close' in req.url:
        req.response('OK')
        door.approach(0)
        light.off()
        return

web.listrout(approach, [
    '/auto_close', '/auto_open'
])

web.active()