import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useDeviceStore } from '../stores/deviceStore'
import { useTokenStore } from '../stores/tokenStore'
import { api } from '../lib/api'

interface FriendDetail {
  id: number
  name: string
  nickname: string | null
  relation_type: string
  contact_frequency: string
  notes: string | null
  health_status: string
  days_since_contact: number | null
  interactions: Interaction[]
}

interface Interaction {
  id: number
  contacted_at: string
  summary: string | null
  next_topics: string[] | null
}

export default function FriendDetail() {
  const { id } = useParams<{ id: string }>()
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const deviceId = useDeviceStore((state) => state.deviceId)
  const { tokensRemaining, freeTrialRemaining, fetchTokens } = useTokenStore()
  
  const [friend, setFriend] = useState<FriendDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [showLogForm, setShowLogForm] = useState(false)
  const [logSummary, setLogSummary] = useState('')
  const [isLogging, setIsLogging] = useState(false)
  
  const [talkStarters, setTalkStarters] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)

  useEffect(() => {
    if (!deviceId || !id) return

    const loadData = async () => {
      try {
        const data = await api.getFriend(deviceId, parseInt(id))
        setFriend(data)
        await fetchTokens(deviceId)
      } catch (err) {
        setError(err instanceof Error ? err.message : t('errors.loadFailed'))
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [deviceId, id, t, fetchTokens])

  const handleLogInteraction = async () => {
    if (!deviceId || !friend) return

    setIsLogging(true)
    try {
      await api.logInteraction(deviceId, friend.id, {
        summary: logSummary.trim() || undefined
      })
      // Reload friend data
      const data = await api.getFriend(deviceId, friend.id)
      setFriend(data)
      setShowLogForm(false)
      setLogSummary('')
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.saveFailed'))
    } finally {
      setIsLogging(false)
    }
  }

  const handleGenerateStarters = async () => {
    if (!deviceId || !friend) return

    setIsGenerating(true)
    setGenerateError(null)

    try {
      const data = await api.getTalkStarters(deviceId, friend.id, i18n.language)
      setTalkStarters(data.starters)
      await fetchTokens(deviceId)
    } catch (err) {
      const message = err instanceof Error ? err.message : t('errors.generic')
      if (message.includes('payment') || message.includes('remaining')) {
        setGenerateError(t('errors.paymentRequired'))
      } else {
        setGenerateError(message)
      }
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDelete = async () => {
    if (!deviceId || !friend) return
    if (!confirm('Are you sure you want to remove this friend?')) return

    try {
      await api.deleteFriend(deviceId, friend.id)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.generic'))
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-warmGray-500">{t('common.loading')}</div>
      </div>
    )
  }

  if (error || !friend) {
    return (
      <div className="card bg-red-50 text-red-600 text-center py-8">
        {error || 'Friend not found'}
      </div>
    )
  }

  const healthColors = {
    green: 'health-green',
    yellow: 'health-yellow',
    red: 'health-red',
  }
  const healthClass = healthColors[friend.health_status as keyof typeof healthColors] || 'health-red'

  return (
    <div className="max-w-2xl mx-auto animate-fadeIn space-y-6">
      {/* Back link */}
      <Link to="/" className="inline-flex items-center gap-2 text-warmGray-500 hover:text-warmGray-700 transition-colors">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        {t('common.back')}
      </Link>

      {/* Friend header */}
      <div className="card">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="font-display text-3xl text-warmGray-800">{friend.name}</h1>
            {friend.nickname && (
              <p className="text-warmGray-500">"{friend.nickname}"</p>
            )}
          </div>
          <div className={`px-4 py-2 rounded-full text-sm font-medium border ${healthClass}`}>
            {t(`health.${friend.health_status}`)}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-warmGray-500">{t('friend.relationType')}:</span>
            <span className="ml-2 font-medium">{t(`friend.types.${friend.relation_type}`)}</span>
          </div>
          <div>
            <span className="text-warmGray-500">{t('friend.contactFrequency')}:</span>
            <span className="ml-2 font-medium">{t(`friend.frequency.${friend.contact_frequency}`)}</span>
          </div>
          <div className="col-span-2">
            <span className="text-warmGray-500">{t('detail.lastContact')}:</span>
            <span className="ml-2 font-medium">
              {friend.days_since_contact !== null
                ? t('detail.daysAgo', { days: friend.days_since_contact })
                : t('detail.neverContacted')}
            </span>
          </div>
        </div>

        {friend.notes && (
          <div className="mt-4 p-4 bg-warmGray-100 rounded-soft text-sm text-warmGray-700">
            {friend.notes}
          </div>
        )}

        <div className="mt-6 flex gap-4">
          <button
            onClick={() => setShowLogForm(!showLogForm)}
            className="btn-primary flex-1"
          >
            {t('detail.logContact')}
          </button>
          <button
            onClick={handleDelete}
            className="px-4 py-2 text-red-500 hover:bg-red-50 rounded-soft transition-colors"
          >
            {t('common.delete')}
          </button>
        </div>

        {/* Log interaction form */}
        {showLogForm && (
          <div className="mt-4 p-4 bg-sage-50 rounded-soft space-y-4">
            <textarea
              value={logSummary}
              onChange={(e) => setLogSummary(e.target.value)}
              placeholder={t('detail.summary')}
              className="w-full px-4 py-3 rounded-soft border border-sage-200 focus:outline-none focus:ring-2 focus:ring-sage-400 resize-none"
              rows={3}
            />
            <button
              onClick={handleLogInteraction}
              disabled={isLogging}
              className="btn-primary w-full disabled:opacity-50"
            >
              {isLogging ? t('common.loading') : t('common.save')}
            </button>
          </div>
        )}
      </div>

      {/* Talk starters */}
      <div className="card">
        <h2 className="font-display text-xl text-warmGray-800 mb-4">
          {t('detail.talkStarters')}
        </h2>

        {talkStarters.length > 0 ? (
          <ul className="space-y-3">
            {talkStarters.map((starter, index) => (
              <li
                key={index}
                className="p-4 bg-gradient-to-r from-sage-50 to-peach-50 rounded-soft text-warmGray-700"
              >
                💬 {starter}
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-center py-6">
            <p className="text-warmGray-500 mb-4">
              {tokensRemaining > 0 || freeTrialRemaining > 0
                ? t('pricing.freeTrials', { count: freeTrialRemaining + tokensRemaining })
                : t('pricing.noTrials')}
            </p>

            {generateError && (
              <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-soft text-sm">
                {generateError}
                {generateError.includes('payment') && (
                  <Link to="/pricing" className="block mt-2 underline">
                    {t('nav.pricing')}
                  </Link>
                )}
              </div>
            )}

            <button
              onClick={handleGenerateStarters}
              disabled={isGenerating || (tokensRemaining === 0 && freeTrialRemaining === 0)}
              className="btn-secondary disabled:opacity-50"
            >
              {isGenerating ? t('common.loading') : t('detail.getTalkStarters')}
            </button>
          </div>
        )}
      </div>

      {/* Interaction history */}
      <div className="card">
        <h2 className="font-display text-xl text-warmGray-800 mb-4">
          {t('detail.interactions')}
        </h2>

        {friend.interactions && friend.interactions.length > 0 ? (
          <ul className="space-y-4">
            {friend.interactions.map((interaction) => (
              <li
                key={interaction.id}
                className="p-4 border border-warmGray-200 rounded-soft"
              >
                <div className="text-sm text-warmGray-500 mb-2">
                  {new Date(interaction.contacted_at).toLocaleDateString(i18n.language)}
                </div>
                {interaction.summary && (
                  <p className="text-warmGray-700">{interaction.summary}</p>
                )}
                {interaction.next_topics && interaction.next_topics.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {interaction.next_topics.map((topic, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-peach-100 text-peach-500 rounded text-xs"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-warmGray-500 text-center py-4">
            {t('detail.noInteractions')}
          </p>
        )}
      </div>
    </div>
  )
}
