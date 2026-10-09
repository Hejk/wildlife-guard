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
