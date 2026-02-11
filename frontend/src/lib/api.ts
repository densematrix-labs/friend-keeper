const API_BASE = '/api/v1'

interface Friend {
  id: number
  name: string
  nickname: string | null
  relation_type: string
  contact_frequency: string
  notes: string | null
  created_at: string
  updated_at: string
  last_interaction: string | null
  health_status: string
  days_since_contact: number | null
}

interface FriendDetail extends Friend {
  interactions: Interaction[]
}

interface Interaction {
  id: number
  friend_id: number
  contacted_at: string
  summary: string | null
  next_topics: string[] | null
  created_at: string
}

interface Dashboard {
  total_friends: number
  need_contact_today: Friend[]
  need_contact_this_week: Friend[]
  healthy_friendships: number
  at_risk_friendships: number
}

interface TokenStatus {
  tokens_remaining: number
  free_trial_remaining: number
}

interface TalkStarters {
  starters: string[]
  context_used: string
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    // Handle both string and object error details
    const errorMessage = typeof data.detail === 'string'
      ? data.detail
      : data.detail?.error || data.detail?.message || `Request failed with status ${response.status}`
    throw new Error(errorMessage)
  }
  return response.json()
}

export const api = {
  // Friends
  getFriends: async (deviceId: string): Promise<Friend[]> => {
    const response = await fetch(`${API_BASE}/friends`, {
      headers: { 'X-Device-Id': deviceId }
    })
    return handleResponse<Friend[]>(response)
  },

  getDashboard: async (deviceId: string): Promise<Dashboard> => {
    const response = await fetch(`${API_BASE}/friends/dashboard`, {
      headers: { 'X-Device-Id': deviceId }
    })
    return handleResponse<Dashboard>(response)
  },

  getFriend: async (deviceId: string, friendId: number): Promise<FriendDetail> => {
    const response = await fetch(`${API_BASE}/friends/${friendId}`, {
      headers: { 'X-Device-Id': deviceId }
    })
    return handleResponse<FriendDetail>(response)
  },

  createFriend: async (deviceId: string, data: {
    name: string
    nickname?: string
    relation_type?: string
    contact_frequency?: string
    notes?: string
  }): Promise<Friend> => {
    const response = await fetch(`${API_BASE}/friends`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Device-Id': deviceId
      },
      body: JSON.stringify(data)
    })
    return handleResponse<Friend>(response)
  },

  deleteFriend: async (deviceId: string, friendId: number): Promise<void> => {
    const response = await fetch(`${API_BASE}/friends/${friendId}`, {
      method: 'DELETE',
      headers: { 'X-Device-Id': deviceId }
    })
    if (!response.ok) {
      throw new Error('Failed to delete friend')
    }
  },

  // Interactions
  logInteraction: async (deviceId: string, friendId: number, data: {
    summary?: string
    next_topics?: string[]
  }): Promise<Interaction> => {
    const response = await fetch(`${API_BASE}/friends/${friendId}/interactions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Device-Id': deviceId
      },
      body: JSON.stringify(data)
    })
    return handleResponse<Interaction>(response)
  },

  // Talk Starters
  getTalkStarters: async (deviceId: string, friendId: number, language: string): Promise<TalkStarters> => {
    const response = await fetch(`${API_BASE}/talk-starters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Device-Id': deviceId
      },
      body: JSON.stringify({ friend_id: friendId, language })
    })
    return handleResponse<TalkStarters>(response)
  },

  // Tokens
  getTokens: async (deviceId: string): Promise<TokenStatus> => {
    const response = await fetch(`${API_BASE}/tokens`, {
      headers: { 'X-Device-Id': deviceId }
    })
    return handleResponse<TokenStatus>(response)
  },

  // Checkout
  createCheckout: async (deviceId: string, productSku: string, successUrl: string): Promise<{ checkout_url: string }> => {
    const response = await fetch(`${API_BASE}/checkout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Device-Id': deviceId
      },
      body: JSON.stringify({
        product_sku: productSku,
        success_url: successUrl,
        device_id: deviceId
      })
    })
    return handleResponse<{ checkout_url: string }>(response)
  }
}
