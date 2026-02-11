import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import FriendCard from '../components/FriendCard'
import LanguageSwitcher from '../components/LanguageSwitcher'

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('FriendCard', () => {
  const mockFriend = {
    id: 1,
    name: 'John Doe',
    nickname: 'Johnny',
    relation_type: 'friend',
    contact_frequency: 'weekly',
    health_status: 'green',
    days_since_contact: 3
  }

  it('renders friend name', () => {
    renderWithRouter(<FriendCard friend={mockFriend} />)
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('renders nickname', () => {
    renderWithRouter(<FriendCard friend={mockFriend} />)
    expect(screen.getByText('"Johnny"')).toBeInTheDocument()
  })

  it('renders health status', () => {
    renderWithRouter(<FriendCard friend={mockFriend} />)
    expect(screen.getByText('health.green')).toBeInTheDocument()
  })

  it('renders days since contact', () => {
    renderWithRouter(<FriendCard friend={mockFriend} />)
    expect(screen.getByText('detail.daysAgo')).toBeInTheDocument()
  })

  it('renders never contacted for null days', () => {
    const neverContactedFriend = { ...mockFriend, days_since_contact: null }
    renderWithRouter(<FriendCard friend={neverContactedFriend} />)
    expect(screen.getByText('detail.neverContacted')).toBeInTheDocument()
  })

  it('links to friend detail', () => {
    renderWithRouter(<FriendCard friend={mockFriend} />)
    const link = screen.getByTestId('friend-card')
    expect(link).toHaveAttribute('href', '/friend/1')
  })

  it('renders relation type', () => {
    renderWithRouter(<FriendCard friend={mockFriend} />)
    expect(screen.getByText('friend.types.friend')).toBeInTheDocument()
  })

  it('applies correct health class for yellow', () => {
    const yellowFriend = { ...mockFriend, health_status: 'yellow' }
    renderWithRouter(<FriendCard friend={yellowFriend} />)
    expect(screen.getByText('health.yellow')).toBeInTheDocument()
  })

  it('applies correct health class for red', () => {
    const redFriend = { ...mockFriend, health_status: 'red' }
    renderWithRouter(<FriendCard friend={redFriend} />)
    expect(screen.getByText('health.red')).toBeInTheDocument()
  })
})

describe('LanguageSwitcher', () => {
  it('renders language switcher button', () => {
    render(<LanguageSwitcher />)
    expect(screen.getByTestId('lang-switcher')).toBeInTheDocument()
  })

  it('opens dropdown on click', () => {
    render(<LanguageSwitcher />)
    const button = screen.getByLabelText('Change language')
    fireEvent.click(button)
    expect(screen.getByText('English')).toBeInTheDocument()
    expect(screen.getByText('中文')).toBeInTheDocument()
    expect(screen.getByText('日本語')).toBeInTheDocument()
  })

  it('shows all 7 languages', () => {
    render(<LanguageSwitcher />)
    const button = screen.getByLabelText('Change language')
    fireEvent.click(button)
    
    expect(screen.getByText('English')).toBeInTheDocument()
    expect(screen.getByText('中文')).toBeInTheDocument()
    expect(screen.getByText('日本語')).toBeInTheDocument()
    expect(screen.getByText('Deutsch')).toBeInTheDocument()
    expect(screen.getByText('Français')).toBeInTheDocument()
    expect(screen.getByText('한국어')).toBeInTheDocument()
    expect(screen.getByText('Español')).toBeInTheDocument()
  })
})
