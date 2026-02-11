import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '../pages/Dashboard'
import AddFriend from '../pages/AddFriend'
import Pricing from '../pages/Pricing'
import PaymentSuccess from '../pages/PaymentSuccess'
import { useDeviceStore } from '../stores/deviceStore'

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('Dashboard', () => {
  beforeEach(() => {
    useDeviceStore.setState({ deviceId: 'test-device', isLoading: false })
  })

  it('shows loading state', () => {
    global.fetch = vi.fn().mockImplementation(() => new Promise(() => {}))
    renderWithRouter(<Dashboard />)
    expect(screen.getByText('common.loading')).toBeInTheDocument()
  })

  it('shows empty state when no friends', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        total_friends: 0,
        need_contact_today: [],
        need_contact_this_week: [],
        healthy_friendships: 0,
        at_risk_friendships: 0
      })
    })

    renderWithRouter(<Dashboard />)
    await waitFor(() => {
      expect(screen.getByText('dashboard.noFriends')).toBeInTheDocument()
    })
  })

  it('shows friends when loaded', async () => {
    const mockFriend = {
      id: 1,
      name: 'Test Friend',
      nickname: null,
      relation_type: 'friend',
      contact_frequency: 'weekly',
      health_status: 'red',
      days_since_contact: 10
    }

    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          total_friends: 1,
          need_contact_today: [mockFriend],
          need_contact_this_week: [],
          healthy_friendships: 0,
          at_risk_friendships: 1
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([mockFriend])
      })

    renderWithRouter(<Dashboard />)
    await waitFor(() => {
      expect(screen.getByText('Test Friend')).toBeInTheDocument()
    })
  })
})

describe('AddFriend', () => {
  beforeEach(() => {
    useDeviceStore.setState({ deviceId: 'test-device', isLoading: false })
  })

  it('renders form fields', () => {
    renderWithRouter(<AddFriend />)
    expect(screen.getByLabelText(/friend.name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/friend.nickname/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/friend.relationType/i)).toBeInTheDocument()
  })

  it('disables submit when name is empty', () => {
    renderWithRouter(<AddFriend />)
    const submitButton = screen.getByText('friend.save')
    expect(submitButton).toBeDisabled()
  })

  it('enables submit when name is filled', () => {
    renderWithRouter(<AddFriend />)
    const nameInput = screen.getByLabelText(/friend.name/i)
    fireEvent.change(nameInput, { target: { value: 'John' } })
    const submitButton = screen.getByText('friend.save')
    expect(submitButton).not.toBeDisabled()
  })
})

describe('Pricing', () => {
  beforeEach(() => {
    useDeviceStore.setState({ deviceId: 'test-device', isLoading: false })
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ tokens_remaining: 5, free_trial_remaining: 1 })
    })
  })

  it('renders pricing title', async () => {
    renderWithRouter(<Pricing />)
    await waitFor(() => {
      expect(screen.getByText('pricing.title')).toBeInTheDocument()
    })
  })

  it('shows all three products', async () => {
    renderWithRouter(<Pricing />)
    await waitFor(() => {
      expect(screen.getByText('pricing.products.starter.name')).toBeInTheDocument()
      expect(screen.getByText('pricing.products.popular.name')).toBeInTheDocument()
      expect(screen.getByText('pricing.products.pro.name')).toBeInTheDocument()
    })
  })

  it('shows token count', async () => {
    renderWithRouter(<Pricing />)
    await waitFor(() => {
      expect(screen.getByText(/pricing.freeTrials/)).toBeInTheDocument()
    })
  })
})

describe('PaymentSuccess', () => {
  beforeEach(() => {
    useDeviceStore.setState({ deviceId: 'test-device', isLoading: false })
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ tokens_remaining: 10, free_trial_remaining: 0 })
    })
  })

  it('renders success message', () => {
    renderWithRouter(<PaymentSuccess />)
    expect(screen.getByText('payment.success')).toBeInTheDocument()
  })

  it('shows back to dashboard link', () => {
    renderWithRouter(<PaymentSuccess />)
    expect(screen.getByText('payment.backToDashboard')).toBeInTheDocument()
  })
})
