import { useCallback, useEffect, useState } from 'react'
import {
  App,
  Button,
  Card,
  Col,
  Divider,
  Form,
  InputNumber,
  Row,
  Slider,
  Switch,
  Tag,
} from 'antd'
import { configApi } from '@/services/api'
import type { ConfigResponse } from '@/types'

interface FormValues {
  volume: number
  trigger_interval: number
  schedule_enabled: boolean
  schedule_interval: number
}

const toBool = (v: string) => v === '1' || v === 'true' || v === 'on'

export default function DeviceConfigPage() {
  const { message } = App.useApp()
  const [form] = Form.useForm<FormValues>()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [deviceOnline, setDeviceOnline] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res: ConfigResponse = await configApi.get()
      setDeviceOnline(res.device_online)
      form.setFieldsValue({
        volume: Number(res.config.volume ?? 80),
        trigger_interval: Number(res.config.trigger_interval ?? 60),
        schedule_enabled: toBool(res.config.schedule_enabled ?? '0'),
        schedule_interval: Number(res.config.schedule_interval ?? 30),
      })
    } finally {
      setLoading(false)
    }
  }, [form])

  useEffect(() => {
    load()
  }, [load])

  const onSave = async (pushToDevice: boolean) => {
    const values = await form.validateFields()
    setSaving(true)
    try {
      const items: Record<string, string> = {
        volume: String(values.volume),
        trigger_interval: String(values.trigger_interval),
        schedule_enabled: values.schedule_enabled ? '1' : '0',
        schedule_interval: String(values.schedule_interval),
      }
      const res = await configApi.update(items, pushToDevice)
      if (pushToDevice) {
        message.success(res.pushed_to_device ? '已保存并同步到设备' : '已保存，但设备下发失败')
      } else {
        message.success('已保存到本地')
      }
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page-container">
      <Card
        title="设备配置"
        loading={loading}
        extra={deviceOnline ? <Tag color="green">设备在线</Tag> : <Tag color="default">设备离线</Tag>}
      >
        <Form form={form} layout="vertical" style={{ maxWidth: 640 }}>
          <Form.Item
            name="volume"
            label="播放音量 (0-100)"
            rules={[{ required: true, message: '请输入音量' }]}
          >
            <Slider min={0} max={100} marks={{ 0: '0', 50: '50', 100: '100' }} />
          </Form.Item>

          <Form.Item
            name="trigger_interval"
            label="触发最小间隔（秒）"
            rules={[{ required: true, message: '请输入触发间隔' }]}
          >
            <InputNumber min={0} max={3600} style={{ width: 200 }} addonAfter="秒" />
          </Form.Item>

          <Divider />

          <Row align="middle">
            <Col>
              <Form.Item name="schedule_enabled" label="定时播放" valuePropName="checked" noStyle>
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="schedule_interval"
            label="定时播放间隔（分钟）"
            style={{ marginTop: 16 }}
          >
            <InputNumber min={1} max={1440} style={{ width: 200 }} addonAfter="分钟" />
          </Form.Item>

          <Divider />

          <Button type="primary" loading={saving} onClick={() => onSave(true)}>
            保存并下发到设备
          </Button>
          <Button style={{ marginLeft: 12 }} loading={saving} onClick={() => onSave(false)}>
            仅保存到本地
          </Button>
        </Form>
      </Card>
    </div>
  )
}
