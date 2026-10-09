// 与后端 Pydantic schema 对齐的 TypeScript 类型

export interface TriggerEvent {
  id: number
  event_time: string
  sensor_id: string
  audio_file?: string | null
  temperature?: number | null
  humidity?: number | null
  battery_voltage?: number | null
  synced_at?: string | null
}

export interface AudioFile {
  id: number
  filename: string
  category?: string | null
  duration_seconds?: number | null
  file_size?: number | null
  status: 'local' | 'synced' | 'deleted' | string
  uploaded_at?: string | null
}

export interface DeviceStatusLatest {
  connected: boolean
  reported_at?: string | null
  battery_voltage?: number | null
  sd_card_total_mb?: number | null
  sd_card_used_mb?: number | null
  uptime_seconds?: number | null
  temperature?: number | null
  humidity?: number | null
  free_heap?: number | null
}

export interface SensorCount {
  sensor_id: string
  count: number
}

export interface DashboardOverview {
  today_count: number
  week_count: number
  total_count: number
  sensor_distribution: SensorCount[]
  recent_events: TriggerEvent[]
}

export interface TrendPoint {
  label: string
  count: number
}

export interface DashboardTrends {
  granularity: string
  points: TrendPoint[]
}

export interface PageResult<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

export interface ConfigResponse {
  config: Record<string, string>
  device_online: boolean
}

export interface ConfigUpdateResponse {
  saved: boolean
  pushed_to_device: boolean
  config: Record<string, string>
}

export interface SyncResponse {
  success: boolean
  synced_events: number
  message: string
}
