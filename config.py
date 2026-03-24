from micropython import const

# --- 硬件引脚定义 ---
PIN_DOOR_UP = 21
PIN_DOOR_DOWN = 19
PIN_DOOR_STOP = 18
PIN_LIGHT = 5

# --- BLE 配置 ---
BLE_NAME = "GC_3523"
# 鉴权 Token
AUTH_TOKEN = "K3Y_3523" 

# --- 自动模式默认时长 (秒) ---
DEFAULT_AUTO_DURATION = 32