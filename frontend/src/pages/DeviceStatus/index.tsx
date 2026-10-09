import { useCallback, useEffect, useState } from 'react'
import {
  App,
  Button,
  Card,
  Col,
  Progress,
  Row,
  Select,
  Space,
  Statistic,
  Tag,
} from 'antd'
import { ApiOutlined, PoweroffOutlined, SyncOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { deviceApi } from '@/services/api'
import { useDeviceStore } from '@/stores/deviceStore'

// 电压 → 电量百分比（18650 单芯 3.0V 空 ~ 4.2V 满）
const batteryPercent = (v?: number | null) => {
  if (v == null) return 0
  const pct = ((v - 3.0) / (4.2 - 3.0)) * 100
  return Math.max(0, Math.min(100, Math.round(pct)))
}

const fmtUptime = (s?: number | null) => {
  if (!s) return '-'
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return `${h}h ${m}m ${sec}s`
}

export default function DeviceStatus() {
  const { message } = App.useApp()
  const { connected, status, fetchStatus, connect, disconnect, sync } = useDeviceStore()
  const [ports, setPorts] = useState<string[]>([])
  const [port, setPort] = useState<string>('auto')
  const [busy, setBusy] = useState(false)

  const loadPorts = useCallback(async () => {
    try {
      const res = await deviceApi.ports()
      setPorts(res.ports)
    } catch {
      /* 忽略：无串口库环境时 */
    }
  }, [])

  useEffect(() => {
    fetchStatus()
    loadPorts()
  }, [fetchStatus, loadPorts])

  const onConnect = async () => {
    setBusy(true)
    try {
      await connect(port, 115200)
      message.success('串口已连接')
    } finally {
      setBusy(false)
    }
  }

  const onDisconnect = async () => {
    setBusy(true)
    try {
      await disconnect()
      message.success('串口已断开')
    } finally {
      setBusy(false)
    }
  }

  const onSync = async () => {
    setBusy(true)
    try {
      const n = await sync()
      message.success(`同步完成，新增 ${n} 条记录`)
    } finally {
      setBusy(false)
    }
  }

  const sdTotal = status?.sd_card_total_mb ?? 0
  const sdUsed = status?.sd_card_used_mb ?? 0
  const sdPct = sdTotal ? Math.round((sdUsed / sdTotal) * 100) : 0

  return (
    <div className="page-container">
      <Card
        title="设备连接"
        extra={connected ? <Tag color="green">已连接</Tag> : <Tag color="default">未连接</Tag>}
        style={{ marginBottom: 16 }}
      >
        <Space wrap>
          <Select
            style={{ width: 220 }}
            value={port}
            onChange={setPort}
            placeholder="选择串口"
            options={[
              { label: 'auto（自动检测）', value: 'auto' },
              ...ports.map((p) => ({ label: p, value: p })),
            ]}
          />
          {!connected ? (
            <Button type="primary" icon={<ApiOutlined />} loading={busy} onClick={onConnect}>
              连接
            </Button>
          ) : (
            <Button danger icon={<PoweroffOutlined />} loading={busy} onClick={onDisconnect}>
              断开
            </Button>
          )}
          <Button icon={<SyncOutlined />} loading={busy} disabled={!connected} onClick={onSync}>
            同步数据
          </Button>
        </Space>
        {!connected && (
          <div style={{ marginTop: 12, color: '#999' }}>
            方案A（USB直连）：巡检时用 USB 线连接笔记本与 ESP32，此处选择对应串口后连接，即可拉取日志、同步音频、下发配置。
          </div>
        )}
      </Card>

      <Row gutter={16}>
        <Col span={6}>
          <Card title="电池电量">
            <Progress
              type="dashboard"
              percent={batteryPercent(status?.battery_voltage)}
              format={() => (status?.battery_voltage ? `${status.battery_voltage}V` : '-')}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card title="SD 卡使用">
            <Progress percent={sdPct} status={sdPct > 90 ? 'exception' : 'normal'} />
            <div style={{ color: '#999' }}>
              {sdUsed} MB / {sdTotal} MB
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card title="运行时长">
            <Statistic value={fmtUptime(status?.uptime_seconds)} valueStyle={{ fontSize: 22 }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card title="环境">
            <Space direction="vertical">
              <Statistic title="温度" value={status?.temperature ?? '-'} suffix="℃" />
              <Statistic title="湿度" value={status?.humidity ?? '-'} suffix="%" />
            </Space>
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}>
        <Space>
          <span>状态上报时间：</span>
          {status?.reported_at ? dayjs(status.reported_at).format('YYYY-MM-DD HH:mm:ss') : '暂无数据'}
        </Space>
      </Card>
    </div>
  )
}
