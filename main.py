# main.py
import _thread
import time
import hardware
import ble_service
import config

# 状态心跳间隔（秒）
HEARTBEAT_INTERVAL = 5

def status_heartbeat_thread(ble_ctrl):
    """
    后台线程：周期性推送状态（心跳包）
    确保手机 App 界面状态始终与硬件同步
    """
    print("[Thread] 状态同步线程已启动")
    while True:
        try:
            # 只有在蓝牙连接成功时才尝试推送
            if ble_ctrl._conn_handle is not None:
                ble_ctrl.push_state()
            
            # 这里的睡眠不会阻塞蓝牙指令接收
            time.sleep(HEARTBEAT_INTERVAL)
        except Exception as e:
            print(f"[Thread] 同步线程异常: {e}")
            time.sleep(2)

def main():
    print(">>> 卷闸门控制器系统启动中...")
    
    # 1. 初始化硬件驱动
    door = hardware.GarageDoor()
    light = hardware.GarageLight()
    
    # 2. 启动 BLE 控制器 (传入硬件实例)
    # 控制器内部会处理蓝牙中断逻辑（运行在底层协议栈线程）
    ble = ble_service.BLEController(door, light)
    
    # 3. 启动后台同步线程 (传入 BLE 实例)
    # 第二个参数必须是元组
    _thread.start_new_thread(status_heartbeat_thread, (ble,))
    
    print(">>> 系统就绪。蓝牙广播名称: {}".format(config.BLE_NAME))
    
    # 4. 主线程进入低功耗循环或执行其他监控任务
    while True:
        # 这里可以跑一些主循环逻辑，比如喂看门狗(WDT)
        # 或者监控 ESP32 的内存/温度
        time.sleep(10)

if __name__ == "__main__":
    main()