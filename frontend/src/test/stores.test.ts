import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useDeviceStore } from '../stores/deviceStore'
import { useTokenStore } from '../stores/tokenStore'

describe('deviceStore', () => {
  beforeEach(() => {
    useDeviceStore.setState({ deviceId: null, isLoading: true })
  })

  it('initializes with null deviceId', () => {
    const state = useDeviceStore.getState()
    expect(state.deviceId).toBeNull()
    expect(state.isLoading).toBe(true)
  })

  it('initDevice sets deviceId', async () => {
    await useDeviceStore.getState().initDevice()
    const state = useDeviceStore.getState()
    expect(state.deviceId).toBe('test-device-id')
    expect(state.isLoading).toBe(false)
  })

  it('does not re-init if already set', async () => {
    useDeviceStore.setState({ deviceId: 'existing-id', isLoading: false })
    await useDeviceStore.getState().initDevice()
    expect(useDeviceStore.getState().deviceId).toBe('existing-id')
  })
})

describe('tokenStore', () => {
  beforeEach(() => {
    useTokenStore.setState({
      tokensRemaining: 0,
      freeTrialRemaining: 3,
      isLoading: true,
      error: null
    })
  })

  it('initializes with default values', () => {
    const state = useTokenStore.getState()
    expect(state.tokensRemaining).toBe(0)
    expect(state.freeTrialRemaining).toBe(3)
  })

  it('fetchTokens updates state', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ tokens_remaining: 10, free_trial_remaining: 0 })
    })

    await useTokenStore.getState().fetchTokens('device-1')
    const state = useTokenStore.getState()
    expect(state.tokensRemaining).toBe(10)
    expect(state.freeTrialRemaining).toBe(0)
    expect(state.isLoading).toBe(false)
  })

  it('fetchTokens handles error', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'))

    await useTokenStore.getState().fetchTokens('device-1')
    const state = useTokenStore.getState()
    expect(state.error).toBe('Network error')
    expect(state.isLoading).toBe(false)
  })
})
