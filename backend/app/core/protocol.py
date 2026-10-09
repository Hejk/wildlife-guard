"""
ESP32 通信协议定义
笔记本 ←USB串口→ ESP32
所有指令和响应均为 JSON 格式，以 \n 分隔。
"""

# 笔记本 → ESP32 的指令
CMD_SYNC_LOGS = "sync_logs"          # 同步触发日志
CMD_GET_STATUS = "get_status"        # 获取设备状态
CMD_UPLOAD_AUDIO = "upload_audio"    # 上传音频文件
CMD_DELETE_AUDIO = "delete_audio"    # 删除音频文件
CMD_LIST_AUDIO = "list_audio"        # 列出SD卡音频文件
CMD_SET_CONFIG = "set_config"        # 更新配置
CMD_GET_CONFIG = "get_config"        # 读取配置

# ESP32 → 笔记本 的响应状态
STATUS_OK = "ok"
STATUS_READY = "ready"
STATUS_ERROR = "error"

# 音频二进制分块传输时的结束标记
AUDIO_EOF = b"\x1A\n"  # Ctrl+Z + 换行，通知设备接收完毕

# 触发事件 JSON 字段（ESP32 上报）
EVENT_FIELDS = (
    "event_time", "sensor_id", "audio_file",
    "temperature", "humidity", "battery_voltage",
)

# 设备状态 JSON 字段（ESP32 上报）
STATUS_FIELDS = (
    "battery_voltage", "sd_total_mb", "sd_used_mb",
    "uptime_seconds", "temperature", "humidity", "free_heap",
)
