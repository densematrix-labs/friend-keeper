import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useDeviceStore } from '../stores/deviceStore'
import { api } from '../lib/api'

export default function AddFriend() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const deviceId = useDeviceStore((state) => state.deviceId)
  
  const [formData, setFormData] = useState({
    name: '',
    nickname: '',
    relation_type: 'friend',
    contact_frequency: 'monthly',
    notes: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!deviceId || !formData.name.trim()) return

    setIsSubmitting(true)
    setError(null)

    try {
      await api.createFriend(deviceId, {
        name: formData.name.trim(),
        nickname: formData.nickname.trim() || undefined,
        relation_type: formData.relation_type,
        contact_frequency: formData.contact_frequency,
        notes: formData.notes.trim() || undefined
      })
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.saveFailed'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto animate-fadeIn">
      <h1 className="font-display text-3xl text-warmGray-800 text-center mb-8">
        {t('friend.add')}
      </h1>

      <form onSubmit={handleSubmit} className="card space-y-6">
        {error && (
          <div className="bg-red-50 text-red-600 px-4 py-3 rounded-soft text-sm">
            {error}
          </div>
        )}

        {/* Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-warmGray-700 mb-2">
            {t('friend.name')} *
          </label>
          <input
            id="name"
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            className="w-full px-4 py-3 rounded-soft border border-warmGray-300 focus:outline-none focus:ring-2 focus:ring-sage-400 focus:border-transparent transition-shadow"
            placeholder="John Doe"
          />
        </div>

        {/* Nickname */}
        <div>
          <label htmlFor="nickname" className="block text-sm font-medium text-warmGray-700 mb-2">
            {t('friend.nickname')}
          </label>
          <input
            id="nickname"
            type="text"
            value={formData.nickname}
            onChange={(e) => setFormData(prev => ({ ...prev, nickname: e.target.value }))}
            className="w-full px-4 py-3 rounded-soft border border-warmGray-300 focus:outline-none focus:ring-2 focus:ring-sage-400 focus:border-transparent transition-shadow"
            placeholder="Johnny"
          />
        </div>

        {/* Relation type */}
        <div>
          <label htmlFor="relation_type" className="block text-sm font-medium text-warmGray-700 mb-2">
            {t('friend.relationType')}
          </label>
          <select
            id="relation_type"
            value={formData.relation_type}
            onChange={(e) => setFormData(prev => ({ ...prev, relation_type: e.target.value }))}
            className="w-full px-4 py-3 rounded-soft border border-warmGray-300 focus:outline-none focus:ring-2 focus:ring-sage-400 focus:border-transparent transition-shadow bg-white"
          >
            <option value="friend">{t('friend.types.friend')}</option>
            <option value="family">{t('friend.types.family')}</option>
            <option value="colleague">{t('friend.types.colleague')}</option>
            <option value="acquaintance">{t('friend.types.acquaintance')}</option>
          </select>
        </div>

        {/* Contact frequency */}
        <div>
          <label htmlFor="contact_frequency" className="block text-sm font-medium text-warmGray-700 mb-2">
            {t('friend.contactFrequency')}
          </label>
          <select
            id="contact_frequency"
            value={formData.contact_frequency}
            onChange={(e) => setFormData(prev => ({ ...prev, contact_frequency: e.target.value }))}
            className="w-full px-4 py-3 rounded-soft border border-warmGray-300 focus:outline-none focus:ring-2 focus:ring-sage-400 focus:border-transparent transition-shadow bg-white"
          >
            <option value="weekly">{t('friend.frequency.weekly')}</option>
            <option value="biweekly">{t('friend.frequency.biweekly')}</option>
            <option value="monthly">{t('friend.frequency.monthly')}</option>
            <option value="quarterly">{t('friend.frequency.quarterly')}</option>
          </select>
        </div>

        {/* Notes */}
        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-warmGray-700 mb-2">
            {t('friend.notes')}
          </label>
          <textarea
            id="notes"
            rows={3}
            value={formData.notes}
            onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
            className="w-full px-4 py-3 rounded-soft border border-warmGray-300 focus:outline-none focus:ring-2 focus:ring-sage-400 focus:border-transparent transition-shadow resize-none"
            placeholder="Likes hiking, has a dog named Max..."
          />
        </div>

        {/* Buttons */}
        <div className="flex gap-4 pt-4">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="btn-secondary flex-1"
          >
            {t('friend.cancel')}
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !formData.name.trim()}
            className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? t('common.loading') : t('friend.save')}
          </button>
        </div>
      </form>
    </div>
  )
}
