import { create } from 'zustand'
import { deviceApi } from '@/services/api'
import type { DeviceStatusLatest } from '@/types'

interface DeviceState {
  connected: boolean
  status: DeviceStatusLatest | null
  loading: boolean
  fetchStatus: () => Promise<void>
  connect: (port: string, baudrate?: number) => Promise<boolean>
  disconnect: () => Promise<void>
  sync: () => Promise<number>
}

export const useDeviceStore = create<DeviceState>((set, get) => ({
  connected: false,
  status: null,
  loading: false,

  fetchStatus: async () => {
    set({ loading: true })
    try {
      const status = await deviceApi.status()
      set({ connected: status.connected, status })
    } finally {
      set({ loading: false })
    }
  },

  connect: async (port, baudrate) => {
    const res = await deviceApi.connect(port, baudrate)
    set({ connected: res.connected })
    await get().fetchStatus()
    return res.connected
  },

  disconnect: async () => {
    await deviceApi.disconnect()
    set({ connected: false })
    await get().fetchStatus()
  },

  sync: async () => {
    const res = await deviceApi.sync()
    await get().fetchStatus()
    return res.synced_events
  },
}))
