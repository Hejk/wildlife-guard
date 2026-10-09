# 智哨 Smart Sentinel

**基于端云协同的农田生态防御系统 · 管理后台 V1**

野猪、鸟类等野生动物在夜间侵入农田，是许多农户一年四季的真实损失。市面上的应对手段要么是人海轮守，要么是孤立的驱赶器械——驱赶了，却不知道"谁来的、什么时候来的、来了几次"。

智哨把这件事闭环起来：**前端**是部署在田间的 ESP32 驱赶主机（红外检测 → 播放驱赶音频 → 记录事件到 SD 卡，固件已完成）；**云端/后台**就是本项目——一个本地即可跑起来的 Web 管理后台，让农户或巡护员在笔记本上打开浏览器，就能查看触发记录与动物活动规律、管理驱赶音频、远程调整设备参数。

V1 采用 **USB 直连近场同步**（方案 A）：巡检时打开设备箱，用 USB 线连接 ESP32 与笔记本，后台自动拉取日志、推送音频、下发配置——**零额外硬件成本，无需联网、无需服务器**。V2 规划升级为 HC-12 无线 / 4G 远程上传，并预留了大模型接口用于动物种类识别与周期分析报告。

> 本文档面向项目评审：按「快速启动」操作，约 5 分钟即可在浏览器中看到完整的管理后台界面。**没有 ESP32 硬件也能演示绝大多数功能**（见「无硬件演示说明」）。

---

## 1. 技术栈一览

| 层 | 选型 |
| --- | --- |
| 前端 | React 18 + TypeScript + Vite 5 + Ant Design 5 + ECharts + Zustand |
| 后端 | Python FastAPI + SQLAlchemy 2 (async) + Uvicorn |
| 数据库 | SQLite 单文件（`database/wildlife.db`），首次启动自动建表并写入默认配置 |
| 设备通信 | pyserial，USB 串口 JSON 行协议（115200 波特率） |
| AI 预留 | 接口化设计，未配置 Key 时优雅降级，不影响主流程 |

## 2. 快速启动

### 2.1 前置要求

- **Python 3.10 或以上**（开发验证环境为 3.11）
- **Node.js 18 或以上**（推荐 20+）
- 验证安装：`python --version`、`node --version`

### 2.2 启动后端（端口 8000）

Windows PowerShell：

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

macOS / Linux 仅需将激活命令换为 `source .venv/bin/activate`。

看到 `Uvicorn running on http://127.0.0.1:8000` 即启动成功。首次启动会自动完成：
- 在 `database/` 下创建 SQLite 数据库并建好 5 张表；
- 写入 4 条默认设备配置（音量、触发间隔、定时播放开关/间隔）。

### 2.3 启动前端（端口 5173）

新开一个终端窗口：

```powershell
cd frontend
npm install
npm run dev
```

### 2.4 访问地址

| 地址 | 内容 |
| --- | --- |
| http://localhost:5173 | 管理后台界面（主入口） |
| http://localhost:8000/docs | Swagger 交互式 API 文档，可直接在线试调用 |
| http://localhost:8000/health | 后端存活探针，返回 `{"status":"ok"}` |

> 环境变量均为可选：将 `backend/.env.example` 复制为 `.env` 可覆盖串口、数据库路径、AI Key 等默认值；不配置也能直接运行。

## 3. 功能验证指引

打开 http://localhost:5173 ，左侧共 5 个页面，对应后台 5 项核心能力：

### 3.1 数据看板
今日 / 本周 / 累计触发次数卡片、近 14 天趋势折线图、传感器触发占比饼图、最近事件列表。数据来自 `/api/dashboard/overview` 与 `/api/dashboard/trends`。

### 3.2 日志查看
触发记录分页表格，支持时间段 + 传感器筛选，点击行查看单条详情，一键**导出 CSV**（Excel 直接打开不乱码）。

### 3.3 音频管理
上传 WAV/MP3 驱赶音频（本地保存 + 登记分类/时长/大小），列表可按分类筛选；设备连接后可**同步到 SD 卡**、**删除时同步清理 SD 卡文件**、以及**「SD 卡对账」**——列出设备侧文件并与本地自动比对差异。

### 3.4 设备配置
音量滑块、触发间隔、定时播放开关与间隔。保存时写入本地库；设备在线时逐条通过串口下发到 ESP32（界面会明确提示"已下发/未下发"）。

### 3.5 设备状态
串口选择与连接/断开、触发日志同步、电池电量仪表盘、SD 卡容量进度条、运行时长与温湿度展示。

### 3.6 API 层验证（可选）
进入 http://localhost:8000/docs ，无需任何工具即可点开任意接口 → `Try it out`。例如：

```bash
curl http://localhost:8000/api/config
# 返回默认配置 {"volume":"80","trigger_interval":"60",...} 及 device_online 标志
```

全部 19 个接口与出入参结构详见 [docs/API.md](docs/API.md)。

## 4. 无硬件演示说明

**没有 ESP32 时，看板/日志/音频/配置四大模块均可完整操作**：数据读写走本地 SQLite，不依赖设备。仅以下操作需要真实串口连接：设备状态页的"连接/同步"、音频"同步到设备/SD 卡对账"、配置的串口下发——未连接时界面与接口会给出明确的中文提示（400 设备未连接），不会报错崩溃。

若希望看板图表立即有数据可看，仓库已内置演示脚本 `backend/seed_demo.py`：在 `backend` 目录下运行 `python seed_demo.py`，即生成近 7 天约 40 条模拟触发记录（演示后删除 `database/wildlife.db` 并重启后端，即可恢复出厂空库状态）：

```python
"""生成演示数据：近 7 天随机触发事件（运行一次即可）"""
import random, sqlite3
from datetime import datetime, timedelta, timezone

random.seed(42)
conn = sqlite3.connect("../database/wildlife.db")
now = datetime.now(timezone.utc).replace(tzinfo=None)
rows = []
for _ in range(40):
    t = now - timedelta(days=random.randint(0, 6), hours=random.randint(18, 23))
    rows.append((t.strftime("%Y-%m-%d %H:%M:%S"), f"SR501_{random.randint(1, 3)}",
                 random.choice(["wild_boar_01.wav", "general_deterrent_01.wav"]),
                 round(random.uniform(18, 30), 1), round(random.uniform(50, 80), 1),
                 round(random.uniform(3.5, 4.1), 2),
                 now.strftime("%Y-%m-%d %H:%M:%S")))
conn.executemany(
    "INSERT INTO trigger_events (event_time, sensor_id, audio_file, temperature,"
    " humidity, battery_voltage, synced_at) VALUES (?,?,?,?,?,?,?)", rows)
conn.commit(); conn.close()
print(f"已写入 {len(rows)} 条演示记录")
```

## 5. 有硬件时的联调路径

1. USB 线连接 ESP32 与笔记本 → 设备状态页选择串口（或 `auto` 自动检测）→ 连接；
2. 点击「同步数据」：后台通过串口 JSON 协议增量拉取 SD 卡触发日志入库，并抓取设备状态快照；
3. 音频管理页上传驱赶音频 → 点击「同步到设备」推送至 SD 卡 → 「SD 卡对账」核对文件一致性；
4. 设备配置页修改音量保存 → 配置实时下发到设备；
5. 手动触发红外传感器 → 设备播放音频并记录事件 → 再次同步后看板/日志呈现新数据。

串口协议约定（指令全集：`sync_logs` / `get_status` / `upload_audio` / `delete_audio` / `list_audio` / `set_config` / `get_config`，JSON 行协议）定义于 `backend/app/core/protocol.py`，固件侧按 [docs/方案蓝图.md](docs/方案蓝图.md) 第六节实现应答即可对接。

## 6. 项目结构

```
├── backend/            # FastAPI 后端
│   ├── app/
│   │   ├── main.py     # 应用入口
│   │   ├── api/        # 6 组路由：dashboard / logs / audio / config / device / ai
│   │   ├── core/       # 配置、数据库、串口客户端、通信协议
│   │   ├── models/     # SQLAlchemy 5 张表
│   │   └── services/   # 同步、音频、AI 业务逻辑
│   └── requirements.txt
├── frontend/           # React + AntD 管理后台
│   └── src/pages/      # 5 个功能页面
├── database/           # SQLite 数据文件（运行时生成）
├── storage/audio/      # 后台本地音频存储
└── docs/               # 方案蓝图、API 文档
```

## 7. 常见问题

| 现象 | 处理 |
| --- | --- |
| 端口被占用 | 后端换端口：`uvicorn app.main:app --port 8001`，同时修改 `frontend/vite.config.ts` 中代理目标 |
| `pip install` 慢 | 国内网络可加 `-i https://pypi.tuna.tsinghua.edu.cn/simple` |
| 看板/日志是空的 | 正常：V1 数据来自设备同步；快速看到效果请使用第 4 节演示数据脚本 |
| 设备状态显示"未连接" | 未插 USB 线时的预期表现，所有非串口功能不受影响 |
| 想重置全部数据 | 停止后端，删除 `database/wildlife.db`，重启后端即自动重建 |

## 8. 演进路线（V2 备忘）

HC-12 无线近场同步 → 4G 模块远程实时上传；SQLite 平滑迁移 MySQL；接入大模型完成动物种类识别与自动分析报告；视需要扩展手机端形态。
