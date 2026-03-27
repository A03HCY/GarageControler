# ble_service.py
import bluetooth
import struct
import json
import time
import machine
from micropython import const
import config

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

class BLEController:
    def __init__(self, door_instance, light_instance):
        self.door = door_instance
        self.light = light_instance
        
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq_handler)
        self._conn_handle = None
        
        self._auto_timer = machine.Timer(1)
        self._is_auto_mode = False # 自动模式运行标志

        # 注册 GATT 服务
        SERVICE_UUID = bluetooth.UUID('0000FF00-0000-1000-8000-00805F9B34FB')
        RX_CHAR = (bluetooth.UUID('0000FF01-0000-1000-8000-00805F9B34FB'), _FLAG_WRITE)
        TX_CHAR = (bluetooth.UUID('0000FF02-0000-1000-8000-00805F9B34FB'), _FLAG_NOTIFY)
        
        ((self._rx_handle, self._tx_handle),) = self._ble.gatts_register_services(((SERVICE_UUID, (RX_CHAR, TX_CHAR)),))
        self._ble.gatts_set_buffer(self._rx_handle, 256, False)
        self._advertise()

    def _advertise(self):
        adv = bytearray()
        adv.extend(struct.pack("BB", 2, 0x01) + b'\x06')
        uuid_bytes = b'\xfb\x34\x9b\x5f\x80\x00\x00\x80\x00\x10\x00\x00\x00\xff\x00\x00'
        adv.extend(struct.pack("BB", len(uuid_bytes) + 1, 0x07) + uuid_bytes)
        
        resp = bytearray()
        name_b = config.BLE_NAME.encode('utf-8')
        resp.extend(struct.pack("BB", len(name_b) + 1, 0x09) + name_b)
        self._ble.gap_advertise(500000, adv_data=adv, resp_data=resp)

    def _irq_handler(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            self._conn_handle, _, _ = data
            self._ble.gap_advertise(None)
            print("[BLE] 已连接")
            
        elif event == _IRQ_CENTRAL_DISCONNECT:
            self._conn_handle = None
            # 安全逻辑：手动模式下断开则停机
            if not self._is_auto_mode and self.door.state != "stopped":
                print("[Security] 手动模式断连，强制停机")
                self.door.stop()
            self._advertise() 

        elif event == _IRQ_GATTS_WRITE:
            conn, attr = data
            if attr == self._rx_handle:
                try:
                    raw = self._ble.gatts_read(self._rx_handle)
                    self._handle_msg(raw)
                except: pass

    def _handle_msg(self, raw):
        try:
            cmd = json.loads(raw.decode('utf-8'))
        except: return

        if cmd.get("token") != config.AUTH_TOKEN: return

        action = cmd.get("action")
        duration = cmd.get("duration", config.DEFAULT_AUTO_DURATION)

        # --- 逻辑分路 ---

        # 1. 自动模式指令 (带防重触发逻辑)
        if action in ["auto_open", "auto_close"]:
            if self._is_auto_mode:
                print(f"[BLE] 自动任务 {self.door.state} 运行中，忽略新指令: {action}")
                return # 直接丢弃，不执行任何操作
            
            self._is_auto_mode = True
            if action == "auto_open":
                self.door.up()
                self.light.on()
            else:
                self.door.down()
            
            # 开启单次定时器
            self._auto_timer.init(period=int(duration * 1000), 
                                 mode=machine.Timer.ONE_SHOT, 
                                 callback=self._on_auto_complete)

        # 2. 手动控制指令 (带熔断逻辑)
        elif action in ["motor_up", "motor_down", "motor_stop"]:
            # 只要手动干预，无论是否在 auto 模式，立即销毁定时器
            self._auto_timer.deinit()
            self._is_auto_mode = False
            
            if action == "motor_up": self.door.up()
            elif action == "motor_down": self.door.down()
            elif action == "motor_stop": self.door.stop()

        # 3. 辅助指令 (不干扰电机运行)
        elif action == "light_on":
            self.light.on()
        elif action == "light_off":
            self.light.off()
        elif action == "status":
            pass

        # 统一状态回复
        self._push_state()

    def _on_auto_complete(self, t):
        """定时器回调：自动任务结束"""
        prev_state = self.door.state
        self.door.stop()
        
        if prev_state == "closing":
            self.light.off()
        
        self._is_auto_mode = False
        self._push_state()
        print("[Timer] Auto-task execution finished safely.")
        
    def push_state(self):
        """公有方法：允许外部线程触发状态推送"""
        self._push_state()

    def _push_state(self):
        state = {"door": self.door.state, "light": self.light.state, "ts": int(time.time())}
        print(state)
        try:
            payload = json.dumps(state).encode('utf-8')
            self._ble.gatts_write(self._tx_handle, payload)
            self._ble.gatts_notify(self._conn_handle, self._tx_handle)
        except: pass