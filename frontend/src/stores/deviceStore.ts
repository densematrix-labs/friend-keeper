import { create } from 'zustand'
import FingerprintJS from '@fingerprintjs/fingerprintjs'

interface DeviceState {
  deviceId: string | null
  isLoading: boolean
  initDevice: () => Promise<void>
}

export const useDeviceStore = create<DeviceState>((set, get) => ({
  deviceId: null,
  isLoading: true,

  initDevice: async () => {
    if (get().deviceId) return

    try {
      const fp = await FingerprintJS.load()
      const result = await fp.get()
      set({ deviceId: result.visitorId, isLoading: false })
    } catch (error) {
      // Fallback to localStorage if fingerprint fails
      let fallbackId = localStorage.getItem('device_id')
      if (!fallbackId) {
        fallbackId = 'fallback-' + Math.random().toString(36).substring(2)
        localStorage.setItem('device_id', fallbackId)
      }
      set({ deviceId: fallbackId, isLoading: false })
    }
  },
}))
