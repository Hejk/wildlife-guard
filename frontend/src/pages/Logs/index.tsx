import { useCallback, useEffect, useState } from 'react'
import { Button, Card, Col, DatePicker, Descriptions, Modal, Row, Select, Space, Table } from 'antd'
import { DownloadOutlined, ReloadOutlined } from '@ant-design/icons'
import dayjs, { Dayjs } from 'dayjs'
import { logsApi, type LogQuery } from '@/services/api'
import type { TriggerEvent } from '@/types'

const SENSOR_OPTIONS = ['SR501_1', 'SR501_2', 'SR501_3'].map((s) => ({ label: s, value: s }))

export default function Logs() {
  const [data, setData] = useState<TriggerEvent[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [sensorId, setSensorId] = useState<string | undefined>(undefined)
  const [range, setRange] = useState<[Dayjs | null, Dayjs | null] | null>(null)
  const [detail, setDetail] = useState<TriggerEvent | null>(null)

  const buildQuery = useCallback((): LogQuery => ({
    page,
    page_size: pageSize,
    sensor_id: sensorId,
    start: range?.[0] ? range[0]!.startOf('day').toISOString() : undefined,
    end: range?.[1] ? range[1]!.endOf('day').toISOString() : undefined,
  }), [page, pageSize, sensorId, range])

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await logsApi.list(buildQuery())
      setData(res.items)
      setTotal(res.total)
    } finally {
      setLoading(false)
    }
  }, [buildQuery])

  useEffect(() => {
    load()
  }, [load])

  const columns = [
    {
      title: '触发时间',
      dataIndex: 'event_time',
      render: (v: string) => (v ? dayjs(v).format('YYYY-MM-DD HH:mm:ss') : '-'),
    },
    { title: '传感器', dataIndex: 'sensor_id' },
    { title: '音频文件', dataIndex: 'audio_file', render: (v: string | null) => v || '-' },
    { title: '温度(℃)', dataIndex: 'temperature', render: (v: number | null) => v ?? '-' },
    { title: '湿度(%)', dataIndex: 'humidity', render: (v: number | null) => v ?? '-' },
    { title: '电压(V)', dataIndex: 'battery_voltage', render: (v: number | null) => v ?? '-' },
  ]

  return (
    <div className="page-container">
      <Card
        title="触发日志"
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={load}>刷新</Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => window.open(logsApi.exportUrl(buildQuery()), '_blank')}
            >
              导出 CSV
            </Button>
          </Space>
        }
      >
        <Row gutter={12} style={{ marginBottom: 16 }}>
          <Col>
            <DatePicker.RangePicker
              value={range as [Dayjs, Dayjs]}
              onChange={(v) => {
                setRange(v as [Dayjs | null, Dayjs | null])
                setPage(1)
              }}
            />
          </Col>
          <Col>
            <Select
              style={{ width: 160 }}
              allowClear
              placeholder="传感器"
              value={sensorId}
              options={SENSOR_OPTIONS}
              onChange={(v) => {
                setSensorId(v)
                setPage(1)
              }}
            />
          </Col>
        </Row>

        <Table
          rowKey="id"
          loading={loading}
          columns={columns}
          dataSource={data}
          onRow={(record) => ({ onClick: () => setDetail(record), style: { cursor: 'pointer' } })}
          pagination={{
            current: page,
            pageSize,
            total,
            showSizeChanger: true,
            onChange: (p, ps) => {
              setPage(p)
              setPageSize(ps)
            },
          }}
        />
      </Card>

      <Modal
        open={!!detail}
        title="事件详情"
        footer={null}
        onCancel={() => setDetail(null)}
      >
        {detail && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="ID">{detail.id}</Descriptions.Item>
            <Descriptions.Item label="触发时间">
              {dayjs(detail.event_time).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="传感器">{detail.sensor_id}</Descriptions.Item>
            <Descriptions.Item label="播放音频">{detail.audio_file || '-'}</Descriptions.Item>
            <Descriptions.Item label="温度">{detail.temperature ?? '-'} ℃</Descriptions.Item>
            <Descriptions.Item label="湿度">{detail.humidity ?? '-'} %</Descriptions.Item>
            <Descriptions.Item label="电池电压">{detail.battery_voltage ?? '-'} V</Descriptions.Item>
            <Descriptions.Item label="同步时间">
              {detail.synced_at ? dayjs(detail.synced_at).format('YYYY-MM-DD HH:mm:ss') : '-'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}
