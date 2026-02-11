import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useDeviceStore } from '../stores/deviceStore'
import { useTokenStore } from '../stores/tokenStore'

export default function PaymentSuccess() {
  const { t } = useTranslation()
  const deviceId = useDeviceStore((state) => state.deviceId)
  const { tokensRemaining, fetchTokens } = useTokenStore()
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    if (deviceId && !loaded) {
      // Small delay to allow webhook to process
      setTimeout(() => {
        fetchTokens(deviceId).then(() => setLoaded(true))
      }, 2000)
    }
  }, [deviceId, fetchTokens, loaded])

  return (
    <div className="max-w-lg mx-auto text-center animate-fadeIn py-12">
      {/* Success animation */}
      <div className="w-24 h-24 mx-auto mb-8 rounded-full bg-sage-100 flex items-center justify-center">
        <span className="text-5xl">🎉</span>
      </div>

      <h1 className="font-display text-3xl text-warmGray-800 mb-4">
        {t('payment.success')}
      </h1>

      {loaded && (
        <p className="text-lg text-warmGray-600 mb-8">
          {t('payment.tokensAdded', { count: tokensRemaining })}
        </p>
      )}

      {!loaded && (
        <p className="text-warmGray-500 mb-8">{t('common.loading')}</p>
      )}

      <Link to="/" className="btn-primary inline-block">
        {t('payment.backToDashboard')}
      </Link>
    </div>
  )
}
