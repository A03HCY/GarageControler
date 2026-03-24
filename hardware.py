import time
from machine import Pin, Timer
import config

class GarageDoor:
    def __init__(self):
        # 初始化引脚，默认低电平 (根据你的逻辑 value=0)
        self._p_up = Pin(config.PIN_DOOR_UP, Pin.OUT, value=0)
        self._p_down = Pin(config.PIN_DOOR_DOWN, Pin.OUT, value=0)
        self._p_stop = Pin(config.PIN_DOOR_STOP, Pin.OUT, value=0)
        
        # 状态追踪
        self.state = "stopped" # stopped, opening, closing
        self._start_time = 0
        self._position_time = 0 # 模拟的高度累积时间
        
        # 专用定时器，用于非阻塞的 Stop 脉冲
        self._pulse_timer = Timer(0)

    def _reset_pins(self):
        self._p_up.value(0)
        self._p_down.value(0)
        # Stop 引脚平常是 0，只有停止时脉冲一下
        self._p_stop.value(0)

    def up(self):
        """触发开门电路"""
        self._reset_pins()
        self._p_up.value(1)
        
        self.state = "opening"
        self._start_time = time.time()
        print("[HW] Door UP")

    def down(self):
        """触发关门电路"""
        self._reset_pins()
        self._p_down.value(1)
        
        self.state = "closing"
        self._start_time = time.time()
        print("[HW] Door DOWN")

    def stop(self):
        """
        非阻塞停止逻辑：
        1. 切断上下行信号
        2. 触发 Stop 脉冲 (ON)
        3. 100ms 后通过回调关闭 Stop 脉冲 (OFF)
        """
        # 1. 切断电源
        self._p_up.value(0)
        self._p_down.value(0)
        
        # 2. 状态计算 (保留你原来的高度计算逻辑)
        now = time.time()
        if self.state == "opening":
            self._position_time += (now - self._start_time)
        elif self.state == "closing":
            self._position_time -= (now - self._start_time)
            if self._position_time < 0: self._position_time = 0
            
        self.state = "stopped"
        self._start_time = 0
        
        # 3. 产生 100ms 脉冲 (模拟按下停止键)
        # 关键：这里不能用 time.sleep，否则 BLE 会断连
        self._p_stop.value(1)
        self._pulse_timer.init(period=100, mode=Timer.ONE_SHOT, callback=self._end_stop_pulse)
        print("[HW] Door STOP (Pulse started)")

    def _end_stop_pulse(self, t):
        """定时器回调：结束脉冲"""
        self._p_stop.value(0)
        print("[HW] Door STOP (Pulse ended)")

class GarageLight:
    def __init__(self):
        self._pin = Pin(config.PIN_LIGHT, Pin.OUT, value=0)
        self.state = "off"

    def on(self):
        self._pin.value(1) # 假设高电平开启
        self.state = "on"
        print("[HW] Light ON")

    def off(self):
        self._pin.value(0)
        self.state = "off"
        print("[HW] Light OFF")