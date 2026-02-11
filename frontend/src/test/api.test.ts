import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '../lib/api'

describe('API', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  describe('handleResponse error handling', () => {
    it('handles string error detail', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Something went wrong' })
      })

      await expect(api.getFriends('device-1')).rejects.toThrow('Something went wrong')
    })

    it('handles object error detail with error field', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 402,
        json: () => Promise.resolve({
          detail: { error: 'No tokens remaining', code: 'payment_required' }
        })
      })

      await expect(api.getFriends('device-1')).rejects.toThrow('No tokens remaining')
    })

    it('handles object error detail with message field', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({
          detail: { message: 'Invalid input' }
        })
      })

      await expect(api.getFriends('device-1')).rejects.toThrow('Invalid input')
    })

    it('never throws [object Object]', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 402,
        json: () => Promise.resolve({
          detail: { error: 'Payment required', code: 'payment_required' }
        })
      })

      try {
        await api.getFriends('device-1')
      } catch (e) {
        expect((e as Error).message).not.toContain('[object Object]')
        expect((e as Error).message).not.toContain('object Object')
      }
    })

    it('falls back to status message when no detail', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error('JSON parse error'))
      })

      await expect(api.getFriends('device-1')).rejects.toThrow('Request failed with status 500')
    })
  })

  describe('getFriends', () => {
    it('returns friends list', async () => {
      const mockFriends = [{ id: 1, name: 'John' }]
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockFriends)
      })

      const result = await api.getFriends('device-1')
      expect(result).toEqual(mockFriends)
      expect(fetch).toHaveBeenCalledWith('/api/v1/friends', {
        headers: { 'X-Device-Id': 'device-1' }
      })
    })
  })

  describe('createFriend', () => {
    it('creates a friend', async () => {
      const newFriend = { id: 1, name: 'Jane' }
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(newFriend)
      })

      const result = await api.createFriend('device-1', { name: 'Jane' })
      expect(result).toEqual(newFriend)
      expect(fetch).toHaveBeenCalledWith('/api/v1/friends', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Device-Id': 'device-1'
        },
        body: JSON.stringify({ name: 'Jane' })
      })
    })
  })

  describe('getTalkStarters', () => {
    it('generates talk starters', async () => {
      const starters = { starters: ['How are you?'], context_used: 'test' }
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(starters)
      })

      const result = await api.getTalkStarters('device-1', 1, 'en')
      expect(result).toEqual(starters)
    })

    it('handles payment required error properly', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 402,
        json: () => Promise.resolve({
          detail: { error: 'No generations remaining. Please purchase more.', code: 'payment_required' }
        })
      })

      try {
        await api.getTalkStarters('device-1', 1, 'en')
        expect.fail('Should have thrown')
      } catch (e) {
        expect((e as Error).message).toBe('No generations remaining. Please purchase more.')
        expect((e as Error).message).not.toContain('[object Object]')
      }
    })
  })

  describe('getTokens', () => {
    it('returns token status', async () => {
      const tokens = { tokens_remaining: 5, free_trial_remaining: 2 }
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(tokens)
      })

      const result = await api.getTokens('device-1')
      expect(result).toEqual(tokens)
    })
  })

  describe('logInteraction', () => {
    it('logs an interaction', async () => {
      const interaction = { id: 1, summary: 'Had coffee' }
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(interaction)
      })

      const result = await api.logInteraction('device-1', 1, { summary: 'Had coffee' })
      expect(result).toEqual(interaction)
    })
  })

  describe('deleteFriend', () => {
    it('deletes a friend', async () => {
      global.fetch = vi.fn().mockResolvedValue({ ok: true })

      await api.deleteFriend('device-1', 1)
      expect(fetch).toHaveBeenCalledWith('/api/v1/friends/1', {
        method: 'DELETE',
        headers: { 'X-Device-Id': 'device-1' }
      })
    })

    it('throws on failure', async () => {
      global.fetch = vi.fn().mockResolvedValue({ ok: false })

      await expect(api.deleteFriend('device-1', 1)).rejects.toThrow('Failed to delete friend')
    })
  })
})
