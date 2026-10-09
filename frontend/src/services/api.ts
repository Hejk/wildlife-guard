import request from './request'
import type {
  AudioFile,
  ConfigResponse,
  ConfigUpdateResponse,
  DashboardOverview,
  DashboardTrends,
  DeviceStatusLatest,
  PageResult,
  SyncResponse,
  TriggerEvent,
} from '@/types'

// ===== 数据看板 =====
export const dashboardApi = {
  overview: () => request.get('/dashboard/overview') as Promise<DashboardOverview>,
  trends: (granularity = 'day', limit = 14) =>
    request.get('/dashboard/trends', {
      params: { granularity, limit },
    }) as Promise<DashboardTrends>,
}

// ===== 日志 =====
export interface LogQuery {
  page?: number
  page_size?: number
  start?: string
  end?: string
  sensor_id?: string
}

export const logsApi = {
  list: (params: LogQuery) =>
    request.get('/logs/events', { params }) as Promise<PageResult<TriggerEvent>>,
  detail: (id: number) =>
    request.get(`/logs/events/${id}`) as Promise<TriggerEvent>,
  exportUrl: (params: LogQuery) => {
    const q = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.append(k, String(v))
    })
    const qs = q.toString()
    return `/api/logs/events/export${qs ? `?${qs}` : ''}`
  },
}

// ===== 音频 =====
export const audioApi = {
  list: () => request.get('/audio/files') as Promise<AudioFile[]>,
  upload: (file: File, category: string) => {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('category', category)
    return request.post('/audio/upload', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }) as Promise<AudioFile>
  },
  remove: (id: number) =>
    request.delete(`/audio/${id}`) as Promise<{
      success: boolean
      status: string
      message: string
      device_deleted: boolean
    }>,
  deviceList: () =>
    request.get('/audio/device-list') as Promise<{ status: string; files: string[] }>,
  sync: (id: number) =>
    request.post(`/audio/sync/${id}`) as Promise<{ success: boolean }>,
}

// ===== 配置 =====
export const configApi = {
  get: () => request.get('/config') as Promise<ConfigResponse>,
  update: (items: Record<string, string>, push_to_device = true) =>
    request.put('/config', { items, push_to_device }) as Promise<ConfigUpdateResponse>,
}

// ===== 设备 / 串口 =====
export const deviceApi = {
  status: () => request.get('/device/status') as Promise<DeviceStatusLatest>,
  ports: () => request.get('/device/ports') as Promise<{ ports: string[] }>,
  connect: (port: string, baudrate?: number) =>
    request.post('/device/connect', { port, baudrate }) as Promise<{
      connected: boolean
      port: string
      baudrate: number
    }>,
  disconnect: () => request.post('/device/disconnect') as Promise<{ connected: boolean }>,
  sync: () => request.post('/device/sync') as Promise<SyncResponse>,
}

// ===== AI 预留 =====
export const aiApi = {
  analyze: (event_id?: number) =>
    request.post('/ai/analyze', { event_id }) as Promise<Record<string, unknown>>,
}
