import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useDeviceStore } from '../stores/deviceStore'
import { useTokenStore } from '../stores/tokenStore'
import { api } from '../lib/api'

const products = [
  { sku: 'starter', tokens: 10, price: '$4.99' },
  { sku: 'popular', tokens: 30, price: '$9.99', popular: true },
  { sku: 'pro', tokens: 100, price: '$24.99' }
]

export default function Pricing() {
  const { t } = useTranslation()
  const deviceId = useDeviceStore((state) => state.deviceId)
  const { tokensRemaining, freeTrialRemaining, fetchTokens } = useTokenStore()
  const [isLoading, setIsLoading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (deviceId) {
      fetchTokens(deviceId)
    }
  }, [deviceId, fetchTokens])

  const handlePurchase = async (sku: string) => {
    if (!deviceId) return

    setIsLoading(sku)
    setError(null)

    try {
      const successUrl = `${window.location.origin}/payment/success`
      const data = await api.createCheckout(deviceId, sku, successUrl)
      window.location.href = data.checkout_url
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.generic'))
      setIsLoading(null)
    }
  }

  const totalAvailable = tokensRemaining + freeTrialRemaining

  return (
    <div className="max-w-4xl mx-auto animate-fadeIn">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="font-display text-4xl text-warmGray-800 mb-4">
          {t('pricing.title')}
        </h1>
        <p className="text-lg text-warmGray-500 max-w-2xl mx-auto">
          {t('pricing.subtitle')}
        </p>

        {/* Current balance */}
        <div className="mt-6 inline-flex items-center gap-2 px-6 py-3 bg-sage-100 rounded-full">
          <span className="text-2xl">✨</span>
          <span className="font-medium text-sage-700">
            {totalAvailable > 0
              ? t('pricing.freeTrials', { count: totalAvailable })
              : t('pricing.noTrials')}
          </span>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-8 p-4 bg-red-50 text-red-600 rounded-soft text-center">
          {error}
        </div>
      )}

      {/* Products */}
      <div className="grid md:grid-cols-3 gap-6">
        {products.map((product) => (
          <div
            key={product.sku}
            className={`card relative ${
              product.popular
                ? 'border-2 border-sage-400 scale-105 shadow-softer'
                : 'border border-warmGray-200'
            }`}
          >
            {product.popular && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-sage-500 text-white text-xs font-semibold rounded-full">
                {t('pricing.popular')}
              </div>
            )}

            <div className="text-center pt-4">
              <h3 className="font-display text-xl text-warmGray-800 mb-2">
                {t(`pricing.products.${product.sku}.name`)}
              </h3>
              <p className="text-sm text-warmGray-500 mb-4">
                {t(`pricing.products.${product.sku}.description`)}
              </p>

              <div className="mb-6">
                <span className="font-display text-4xl text-warmGray-800">{product.price}</span>
              </div>

              <ul className="space-y-3 mb-8 text-sm text-warmGray-600">
                <li className="flex items-center justify-center gap-2">
                  <span className="text-sage-500">✓</span>
                  {t('pricing.features.starters', { count: product.tokens })}
                </li>
                <li className="flex items-center justify-center gap-2">
                  <span className="text-sage-500">✓</span>
                  {t('pricing.features.languages')}
                </li>
                <li className="flex items-center justify-center gap-2">
                  <span className="text-sage-500">✓</span>
                  {t('pricing.features.instant')}
                </li>
              </ul>

              <button
                onClick={() => handlePurchase(product.sku)}
                disabled={isLoading !== null}
                className={`w-full py-3 rounded-soft font-semibold transition-all ${
                  product.popular
                    ? 'bg-sage-500 text-white hover:bg-sage-600'
                    : 'bg-warmGray-100 text-warmGray-700 hover:bg-warmGray-200'
                } disabled:opacity-50`}
              >
                {isLoading === product.sku ? t('common.loading') : t('common.save')}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Trust badges */}
      <div className="mt-12 text-center text-sm text-warmGray-500">
        <div className="flex items-center justify-center gap-6">
          <span>🔒 Secure payment</span>
          <span>💳 All cards accepted</span>
          <span>⚡ Instant delivery</span>
        </div>
      </div>
    </div>
  )
}
