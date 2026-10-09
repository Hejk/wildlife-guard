# 智哨（Smart Sentinel）管理后台 · API 文档（V1）

- Base URL（开发）：`http://localhost:8000`
- 前端通过 Vite 代理访问：`http://localhost:5173/api/...` → 后端
- 交互式文档（Swagger）：`http://localhost:8000/docs`
- 通信模式：方案A（USB 直连）。串口相关接口在未连接 ESP32 时会返回 400/502，其余数据接口不受影响。

统一约定：
- 时间字段为 ISO8601 字符串（后端以 UTC 存储）。
- 串口类操作需先 `POST /api/device/connect`。

---

## 健康检查

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 服务信息 |
| GET | `/health` | 存活探针 `{ "status": "ok" }` |

---

## 数据看板 `/api/dashboard`

### GET /api/dashboard/overview
返回：
```json
{
  "today_count": 0,
  "week_count": 0,
  "total_count": 0,
  "sensor_distribution": [{ "sensor_id": "SR501_1", "count": 0 }],
  "recent_events": [
    { "id": 1, "event_time": "...", "sensor_id": "SR501_1", "audio_file": "...",
      "temperature": 25.5, "humidity": 60.2, "battery_voltage": 3.72, "synced_at": "..." }
  ]
}
```

### GET /api/dashboard/trends
查询参数：`granularity` = `day`|`week`|`month`（默认 day），`limit`（默认 14，1-365）
返回：`{ "granularity": "day", "points": [{ "label": "2026-10-09", "count": 3 }] }`

---

## 日志管理 `/api/logs`

### GET /api/logs/events
分页查询。参数：`page`(默认1)、`page_size`(默认20,最大200)、`start`、`end`、`sensor_id`
返回：`{ "total": 0, "page": 1, "page_size": 20, "items": [ <TriggerEvent> ] }`

### GET /api/logs/events/{event_id}
返回单条 `<TriggerEvent>`；不存在返回 404。

### GET /api/logs/events/export
按 `start`/`end`/`sensor_id` 导出 CSV（`text/csv`，UTF-8 BOM，附件下载）。
> 注意：路由 `/export` 先于 `/{event_id}` 注册。

---

## 音频管理 `/api/audio`

### GET /api/audio/files
返回 `<AudioFile>[]`。

### POST /api/audio/upload
`multipart/form-data`：`file`(必填)、`category`(默认「通用驱赶」)。
保存到本地 `storage/audio/`，登记为 `status=local`，尽力解析 WAV 时长。返回 `<AudioFile>`。

### DELETE /api/audio/{audio_id}
删除本地磁盘文件；设备在线时同步删除 SD 卡文件（失败不阻塞）。记录保留并置 `status=deleted`（同名重传可复活）。
返回：`{ "success": true, "status": "ok", "message": "已删除 <文件名>", "device_deleted": false }`

### GET /api/audio/device-list
列出 SD 卡上的音频文件，供与本地对账。需已连接设备，否则 400；串口异常 502。
返回：`{ "status": "ok", "files": ["a.wav", "b.wav"] }`

### POST /api/audio/sync/{audio_id}
通过串口将本地音频推送到 ESP32 SD 卡。需已连接设备，否则 400；串口异常 502。
成功返回 `{ "success": true }`，记录置 `status=synced`。

---

## 设备配置 `/api/config`

### GET /api/config
返回：`{ "config": { "volume": "80", "trigger_interval": "60", "schedule_enabled": "0", "schedule_interval": "30" }, "device_online": false }`

### PUT /api/config
请求体：
```json
{ "items": { "volume": "95" }, "push_to_device": true }
```
- 始终 upsert 到本地库；`push_to_device=true` 且设备在线时逐条 `set_config` 下发。
返回：`{ "saved": true, "pushed_to_device": false, "config": { ... } }`

---

## 设备状态与串口 `/api/device`

### GET /api/device/ports
返回系统可用串口：`{ "ports": ["COM3"] }`

### POST /api/device/connect
请求体：`{ "port": "auto", "baudrate": 115200 }`（`baudrate` 可省略取默认）
成功：`{ "connected": true, "port": "COM3", "baudrate": 115200 }`；失败 400。

### POST /api/device/disconnect
返回：`{ "connected": false }`

### GET /api/device/status
返回最近一次状态快照 + 当前连接标志：
```json
{ "connected": false, "reported_at": "...", "battery_voltage": 3.72,
  "sd_card_total_mb": 32256, "sd_card_used_mb": 1024, "uptime_seconds": 3600,
  "temperature": 25.5, "humidity": 60.2, "free_heap": null }
```

### POST /api/device/sync
触发串口增量同步日志 + 拉取设备状态并落库。需已连接设备，否则 400。
返回：`{ "success": true, "synced_events": 12, "message": "同步完成" }`

---

## AI 预留 `/api/ai`

### POST /api/ai/analyze
请求体：`{ "event_id": 1 }`（可省略）
- 未配置 `AI_API_KEY`：`{ "status": "disabled", "message": "AI API key not configured" }`
- 已配置但能力待接入：501 `{ "detail": "AI 分析能力待接入" }`

---

## 数据模型

- **TriggerEvent**：`id, event_time, sensor_id, audio_file, temperature, humidity, battery_voltage, synced_at`
- **AudioFile**：`id, filename, category, duration_seconds, file_size, status(local/synced/deleted), uploaded_at`
- **DeviceConfig**：`config_key, config_value, updated_at`
- **DeviceStatus**：`id, reported_at, battery_voltage, sd_card_total_mb, sd_card_used_mb, uptime_seconds, temperature, humidity`
- **AIAnalysis**（预留）：`id, event_id, ai_model, analysis_result, confidence, created_at`
