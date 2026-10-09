"""ESP32 串口通信客户端 - USB 直连模式（方案A）。

实现说明：方案蓝图原用 aioserial，但 PyPI 上并无该稳定包；
此处采用标准 pyserial + asyncio.to_thread 包装阻塞调用，工程上更可靠，
并加线程锁保证串口指令串行执行。
"""
import asyncio
import json
from typing import Optional

import serial
import serial.tools.list_ports

from app.core.config import get_settings
from app.core import protocol


class SerialClient:
    def __init__(self, port: str = "auto", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        self._lock = asyncio.Lock()  # 保证同一时刻只有一条指令在总线上往返

    # ---------- 连接管理 ----------
    @staticmethod
    def list_ports() -> list[str]:
        return [p.device for p in serial.tools.list_ports.comports()]

    async def connect(self) -> bool:
        s = get_settings()
        self.port = self.port if self.port != "auto" else s.serial_port
        self.baudrate = self.baudrate or s.serial_baudrate
        try:
            if self.port == "auto" or not self.port:
                ports = self.list_ports()
                if not ports:
                    return False
                self.port = ports[0]

            def _open():
                return serial.Serial(port=self.port, baudrate=self.baudrate, timeout=3.0)

            self.serial = await asyncio.to_thread(_open)
            self.connected = True
            return True
        except Exception as e:
            print(f"串口连接失败: {e}")
            self.connected = False
            self.serial = None
            return False

    async def disconnect(self) -> None:
        if self.serial:
            try:
                await asyncio.to_thread(self.serial.close)
            except Exception:
                pass
        self.serial = None
        self.connected = False

    # ---------- 指令收发 ----------
    async def _write(self, data: bytes) -> None:
        await asyncio.to_thread(self.serial.write, data)
        await asyncio.to_thread(self.serial.flush)

    async def _readline(self) -> bytes:
        return await asyncio.to_thread(self.serial.readline)

    async def send_command(self, cmd: dict) -> dict:
        if not self.connected or not self.serial:
            raise ConnectionError("串口未连接")
        async with self._lock:
            await self._write((json.dumps(cmd, ensure_ascii=False) + "\n").encode("utf-8"))
            resp = await self._readline()
            if not resp:
                raise TimeoutError("ESP32 响应超时")
            return json.loads(resp.decode("utf-8").strip())

    # ---------- 高层业务 ----------
    async def sync_logs(self, since: str = "") -> list:
        resp = await self.send_command({"cmd": protocol.CMD_SYNC_LOGS, "since": since})
        return resp.get("logs", [])

    async def get_status(self) -> dict:
        return await self.send_command({"cmd": protocol.CMD_GET_STATUS})

    async def upload_audio(self, filename: str, file_data: bytes, chunk: int = 1024) -> bool:
        # 1) 通知设备准备接收
        resp = await self.send_command({
            "cmd": protocol.CMD_UPLOAD_AUDIO,
            "filename": filename,
            "size": len(file_data),
        })
        if resp.get("status") != protocol.STATUS_READY:
            return False
        # 2) 分块发送二进制数据 + EOF
        if not self.connected or not self.serial:
            raise ConnectionError("串口未连接")
        async with self._lock:
            for i in range(0, len(file_data), chunk):
                await self._write(file_data[i:i + chunk])
            await self._write(protocol.AUDIO_EOF)
            # 3) 等待确认
            line = await self._readline()
            result = json.loads(line.decode("utf-8").strip())
            return result.get("status") == protocol.STATUS_OK

    async def delete_audio(self, filename: str) -> bool:
        resp = await self.send_command({"cmd": protocol.CMD_DELETE_AUDIO, "filename": filename})
        return resp.get("status") == protocol.STATUS_OK

    async def list_audio(self) -> list:
        """列出 SD 卡上的音频文件，供后台与本地对账。"""
        resp = await self.send_command({"cmd": protocol.CMD_LIST_AUDIO})
        return resp.get("files", [])

    async def set_config(self, key: str, value: str) -> bool:
        resp = await self.send_command({"cmd": protocol.CMD_SET_CONFIG, "key": key, "value": value})
        return resp.get("status") == protocol.STATUS_OK

    async def get_config(self) -> dict:
        resp = await self.send_command({"cmd": protocol.CMD_GET_CONFIG})
        return resp.get("config", {})


# 全局串口客户端实例
serial_client = SerialClient()
