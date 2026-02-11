import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useDeviceStore } from '../stores/deviceStore'
import { api } from '../lib/api'
import FriendCard from '../components/FriendCard'

interface Dashboard {
  total_friends: number
  need_contact_today: Friend[]
  need_contact_this_week: Friend[]
  healthy_friendships: number
  at_risk_friendships: number
}

interface Friend {
  id: number
  name: string
  nickname: string | null
  relation_type: string
  contact_frequency: string
  health_status: string
  days_since_contact: number | null
}

export default function Dashboard() {
  const { t } = useTranslation()
  const deviceId = useDeviceStore((state) => state.deviceId)
  const [dashboard, setDashboard] = useState<Dashboard | null>(null)
  const [allFriends, setAllFriends] = useState<Friend[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!deviceId) return

    const loadData = async () => {
      try {
        const [dashboardData, friendsData] = await Promise.all([
          api.getDashboard(deviceId),
          api.getFriends(deviceId)
        ])
        setDashboard(dashboardData)
        setAllFriends(friendsData)
      } catch (err) {
        setError(err instanceof Error ? err.message : t('errors.loadFailed'))
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [deviceId, t])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-warmGray-500">{t('common.loading')}</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card bg-red-50 text-red-600 text-center py-8">
        {error}
      </div>
    )
  }

  const healthyFriends = allFriends.filter(f => f.health_status === 'green')

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="text-center">
        <h1 className="font-display text-4xl text-warmGray-800 mb-2">
          {t('dashboard.title')}
        </h1>
        <p className="text-warmGray-500">{t('dashboard.subtitle')}</p>
      </div>

      {/* Stats */}
      {dashboard && dashboard.total_friends > 0 && (
        <div className="grid grid-cols-2 gap-4">
          <div className="card text-center">
            <div className="text-3xl font-display text-sage-600 mb-1">
              {dashboard.healthy_friendships}
            </div>
            <div className="text-sm text-warmGray-500">
              {t('dashboard.healthyCount', { count: dashboard.healthy_friendships })}
            </div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-display text-peach-500 mb-1">
              {dashboard.at_risk_friendships}
            </div>
            <div className="text-sm text-warmGray-500">
              {t('dashboard.atRiskCount', { count: dashboard.at_risk_friendships })}
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {allFriends.length === 0 && (
        <div className="card text-center py-12">
          <div className="text-6xl mb-4">🌱</div>
          <h2 className="font-display text-2xl text-warmGray-700 mb-2">
            {t('dashboard.noFriends')}
          </h2>
          <p className="text-warmGray-500 mb-6">{t('dashboard.addFirst')}</p>
          <Link to="/add" className="btn-primary inline-block">
            {t('friend.add')}
          </Link>
        </div>
      )}

      {/* Needs attention */}
      {dashboard && dashboard.need_contact_today.length > 0 && (
        <section>
          <h2 className="font-display text-xl text-warmGray-800 mb-4 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-400"></span>
            {t('dashboard.needsAttention')}
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {dashboard.need_contact_today.map((friend) => (
              <FriendCard key={friend.id} friend={friend} />
            ))}
          </div>
        </section>
      )}

      {/* Coming up */}
      {dashboard && dashboard.need_contact_this_week.length > 0 && (
        <section>
          <h2 className="font-display text-xl text-warmGray-800 mb-4 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-yellow-400"></span>
            {t('dashboard.comingUp')}
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {dashboard.need_contact_this_week.map((friend) => (
              <FriendCard key={friend.id} friend={friend} />
            ))}
          </div>
        </section>
      )}

      {/* All good */}
      {healthyFriends.length > 0 && (
        <section>
          <h2 className="font-display text-xl text-warmGray-800 mb-4 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-sage-400"></span>
            {t('dashboard.allGood')}
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {healthyFriends.map((friend) => (
              <FriendCard key={friend.id} friend={friend} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
