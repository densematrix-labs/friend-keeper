import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

interface Friend {
  id: number
  name: string
  nickname: string | null
  relation_type: string
  contact_frequency: string
  health_status: string
  days_since_contact: number | null
}

interface FriendCardProps {
  friend: Friend
}

export default function FriendCard({ friend }: FriendCardProps) {
  const { t } = useTranslation()

  const healthColors = {
    green: 'health-green',
    yellow: 'health-yellow',
    red: 'health-red',
  }

  const healthClass = healthColors[friend.health_status as keyof typeof healthColors] || 'health-red'

  const getRelationEmoji = (type: string) => {
    const emojis: Record<string, string> = {
      friend: '👋',
      family: '👨‍👩‍👧',
      colleague: '💼',
      acquaintance: '🤝',
    }
    return emojis[type] || '👋'
  }

  return (
    <Link
      to={`/friend/${friend.id}`}
      className="card block group hover:scale-[1.02] transition-transform"
      data-testid="friend-card"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-sage-200 to-peach-200 flex items-center justify-center text-2xl shadow-soft">
            {getRelationEmoji(friend.relation_type)}
          </div>
          <div>
            <h3 className="font-display text-lg text-warmGray-800 group-hover:text-sage-600 transition-colors">
              {friend.name}
            </h3>
            {friend.nickname && (
              <p className="text-sm text-warmGray-500">"{friend.nickname}"</p>
            )}
          </div>
        </div>

        <div className={`px-3 py-1 rounded-full text-xs font-medium border ${healthClass}`}>
          {t(`health.${friend.health_status}`)}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between text-sm text-warmGray-500">
        <span>{t(`friend.types.${friend.relation_type}`)}</span>
        <span>
          {friend.days_since_contact !== null
            ? t('detail.daysAgo', { days: friend.days_since_contact })
            : t('detail.neverContacted')}
        </span>
      </div>
    </Link>
  )
}
