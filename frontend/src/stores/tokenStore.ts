import { create } from 'zustand'
import { api } from '../lib/api'

interface TokenState {
  tokensRemaining: number
  freeTrialRemaining: number
  isLoading: boolean
  error: string | null
  fetchTokens: (deviceId: string) => Promise<void>
}

export const useTokenStore = create<TokenState>((set) => ({
  tokensRemaining: 0,
  freeTrialRemaining: 3,
  isLoading: true,
  error: null,

  fetchTokens: async (deviceId: string) => {
    set({ isLoading: true, error: null })
    try {
      const data = await api.getTokens(deviceId)
      set({
        tokensRemaining: data.tokens_remaining,
        freeTrialRemaining: data.free_trial_remaining,
        isLoading: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load tokens',
        isLoading: false,
      })
    }
  },
}))
