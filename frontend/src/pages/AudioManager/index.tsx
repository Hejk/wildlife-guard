import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  App,
  Button,
  Card,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  Upload,
} from 'antd'
import {
  UploadOutlined,
  SyncOutlined,
  DeleteOutlined,
  FileSearchOutlined,
} from '@ant-design/icons'
import type { UploadFile as AntUploadFile } from 'antd'
import dayjs from 'dayjs'
import { audioApi } from '@/services/api'
import { useDeviceStore } from '@/stores/deviceStore'
import type { AudioFile } from '@/types'

const CATEGORIES = ['通用驱赶', '鸟类', '兽类', '野猪', '其他']

const statusTag = (status: string) => {
  if (status === 'synced') return <Tag color="green">已同步设备</Tag>
  if (status === 'deleted') return <Tag color="red">已删除</Tag>
  return <Tag color="orange">仅本地</Tag>
}

export default function AudioManager() {
  const { message } = App.useApp()
  const connected = useDeviceStore((s) => s.connected)
  const [data, setData] = useState<AudioFile[]>([])
  const [loading, setLoading] = useState(false)
  const [category, setCategory] = useState<string>('通用驱赶')
  const [filter, setFilter] = useState<string | undefined>(undefined)
  const [reconcileOpen, setReconcileOpen] = useState(false)
  const [deviceFiles, setDeviceFiles] = useState<string[]>([])
  const [reconciling, setReconciling] = useState(false)
  const fileRef = useRef<File | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      setData(await audioApi.list())
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const filtered = useMemo(
    () => (filter ? data.filter((d) => d.category === filter) : data),
    [data, filter],
  )

  const handleUpload = async () => {
    if (!fileRef.current) {
      message.warning('请先选择音频文件')
      return
    }
    const rec = await audioApi.upload(fileRef.current, category)
    message.success(`已保存：${rec.filename}`)
    fileRef.current = null
    load()
  }

  const handleSync = async (id: number) => {
    await audioApi.sync(id)
    message.success('已同步到设备 SD 卡')
    load()
  }

  const handleDelete = async (id: number) => {
    const res = await audioApi.remove(id)
    message.success(
      res.device_deleted
        ? `${res.message}（SD 卡已同步删除）`
        : `${res.message}（设备未连接或删除失败，SD 卡文件保留）`,
    )
    load()
  }

  const handleReconcile = async () => {
    setReconciling(true)
    try {
      const res = await audioApi.deviceList()
      setDeviceFiles(res.files)
      setReconcileOpen(true)
    } finally {
      setReconciling(false)
    }
  }

  // 对账用：本地当前有效文件名（排除已删除记录）
  const localNames = useMemo(
    () => new Set(data.filter((d) => d.status !== 'deleted').map((d) => d.filename)),
    [data],
  )

  const deviceColumns = [
    { title: 'SD 卡文件名', dataIndex: 'filename', key: 'filename' },
    {
      title: '对账结果',
      key: 'match',
      render: (_: unknown, r: { filename: string }) =>
        localNames.has(r.filename) ? (
          <Tag color="green">本地存在</Tag>
        ) : (
          <Tag color="warning">仅设备侧</Tag>
        ),
    },
  ]

  const columns = [
    { title: '文件名', dataIndex: 'filename', key: 'filename' },
    { title: '分类', dataIndex: 'category', key: 'category' },
    {
      title: '时长',
      dataIndex: 'duration_seconds',
      key: 'duration',
      render: (v: number | null) => (v != null ? `${v}s` : '-'),
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'size',
      render: (v: number | null) => (v != null ? `${(v / 1024).toFixed(1)} KB` : '-'),
    },
    { title: '状态', dataIndex: 'status', key: 'status', render: statusTag },
    {
      title: '上传时间',
      dataIndex: 'uploaded_at',
      key: 'uploaded_at',
      render: (v: string | null) => (v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '-'),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: unknown, r: AudioFile) => (
        <Space>
          <Button
            size="small"
            icon={<SyncOutlined />}
            disabled={!connected}
            onClick={() => handleSync(r.id)}
          >
            同步到设备
          </Button>
          <Popconfirm title="确认删除该音频？" onConfirm={() => handleDelete(r.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="page-container">
      <Card
        title="上传音频"
        extra={
          <Space>
            {!connected && <Tag color="default">设备未连接：仅保存到本地，无法同步到 SD 卡</Tag>}
            <Button
              icon={<FileSearchOutlined />}
              disabled={!connected}
              loading={reconciling}
              onClick={handleReconcile}
            >
              SD 卡对账
            </Button>
          </Space>
        }
      >
        <Space wrap style={{ marginBottom: 12 }}>
          <Upload
            beforeUpload={(file: AntUploadFile) => {
              fileRef.current = file as unknown as File
              return false // 阻止自动上传，手动提交
            }}
            maxCount={1}
            showUploadList={false}
            accept=".wav,.mp3,.aac,.ogg"
          >
            <Button icon={<UploadOutlined />}>选择文件</Button>
          </Upload>
          <Select
            style={{ width: 160 }}
            value={category}
            onChange={setCategory}
            options={CATEGORIES.map((c) => ({ label: c, value: c }))}
          />
          <Button type="primary" onClick={handleUpload}>
            上传保存
          </Button>
        </Space>

        <div style={{ marginBottom: 12 }}>
          <Input
            style={{ width: 200 }}
            placeholder="分类筛选"
            allowClear
            onChange={(e) => setFilter(e.target.value || undefined)}
          />
        </div>

        <Table
          rowKey="id"
          loading={loading}
          columns={columns}
          dataSource={filtered}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="SD 卡音频对账"
        open={reconcileOpen}
        onCancel={() => setReconcileOpen(false)}
        footer={null}
        width={560}
      >
        <Table
          rowKey="filename"
          size="small"
          columns={deviceColumns}
          dataSource={deviceFiles.map((f) => ({ filename: f }))}
          pagination={false}
          locale={{ emptyText: 'SD 卡上没有音频文件' }}
        />
      </Modal>
    </div>
  )
}
