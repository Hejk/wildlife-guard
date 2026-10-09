import { useCallback, useEffect, useState } from 'react'
import { Card, Col, Empty, Row, Spin, Statistic, Table, Tag } from 'antd'
import dayjs from 'dayjs'
import EChart from '@/components/EChart'
import { dashboardApi } from '@/services/api'
import type { DashboardOverview, DashboardTrends, TriggerEvent } from '@/types'

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [overview, setOverview] = useState<DashboardOverview | null>(null)
  const [trends, setTrends] = useState<DashboardTrends | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [ov, tr] = await Promise.all([
        dashboardApi.overview(),
        dashboardApi.trends('day', 14),
      ])
      setOverview(ov)
      setTrends(tr)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const trendOption = {
    tooltip: { trigger: 'axis' as const },
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: {
      type: 'category' as const,
      data: trends?.points.map((p) => p.label) ?? [],
    },
    yAxis: { type: 'value' as const, minInterval: 1 },
    series: [
      {
        name: '触发次数',
        type: 'line' as const,
        smooth: true,
        areaStyle: { opacity: 0.15 },
        data: trends?.points.map((p) => p.count) ?? [],
      },
    ],
  }

  const pieOption = {
    tooltip: { trigger: 'item' as const },
    legend: { bottom: 0 },
    series: [
      {
        name: '传感器分布',
        type: 'pie' as const,
        radius: ['40%', '65%'],
        data: (overview?.sensor_distribution ?? []).map((s) => ({
          name: s.sensor_id,
          value: s.count,
        })),
      },
    ],
  }

  const columns = [
    {
      title: '触发时间',
      dataIndex: 'event_time',
      key: 'event_time',
      render: (v: string) => (v ? dayjs(v).format('YYYY-MM-DD HH:mm:ss') : '-'),
    },
    { title: '传感器', dataIndex: 'sensor_id', key: 'sensor_id' },
    {
      title: '音频',
      dataIndex: 'audio_file',
      key: 'audio_file',
      render: (v: string | null) => v || '-',
    },
    {
      title: '温度/湿度',
      key: 'env',
      render: (_: unknown, r: TriggerEvent) =>
        `${r.temperature ?? '-'}℃ / ${r.humidity ?? '-'}%`,
    },
    {
      title: '电压',
      key: 'battery',
      render: (_: unknown, r: TriggerEvent) =>
        r.battery_voltage ? `${r.battery_voltage}V` : '-',
    },
  ]

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!overview) {
    return <Empty description="暂无数据" />
  }

  return (
    <div className="page-container">
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic title="今日触发" value={overview.today_count} suffix="次" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="本周触发" value={overview.week_count} suffix="次" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="累计触发" value={overview.total_count} suffix="次" />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={16}>
          <Card title="近 14 天触发趋势">
            <EChart option={trendOption} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="传感器触发占比">
            {overview.sensor_distribution.length ? (
              <EChart option={pieOption} />
            ) : (
              <Empty description="暂无数据" />
            )}
          </Card>
        </Col>
      </Row>

      <Card
        title="最近事件"
        style={{ marginTop: 16 }}
        extra={<Tag color="blue">最新 {overview.recent_events.length} 条</Tag>}
      >
        <Table
          rowKey="id"
          size="small"
          columns={columns}
          dataSource={overview.recent_events}
          pagination={false}
        />
      </Card>
    </div>
  )
}
