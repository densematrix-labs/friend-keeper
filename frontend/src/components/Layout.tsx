import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { t } = useTranslation()
  const location = useLocation()

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-cream-100/80 backdrop-blur-md border-b border-warmGray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-sage-300 to-peach-300 flex items-center justify-center shadow-soft group-hover:scale-105 transition-transform">
                <span className="text-lg">🤝</span>
              </div>
              <div>
                <h1 className="font-display text-xl text-warmGray-800">{t('app.name')}</h1>
                <p className="text-xs text-warmGray-500 hidden sm:block">{t('app.tagline')}</p>
              </div>
            </Link>

            <nav className="flex items-center gap-2 sm:gap-4">
              <Link
                to="/"
                className={`px-3 py-2 rounded-soft text-sm font-medium transition-colors ${
                  location.pathname === '/'
                    ? 'bg-sage-100 text-sage-600'
                    : 'text-warmGray-600 hover:bg-warmGray-100'
                }`}
              >
                {t('nav.dashboard')}
              </Link>
              <Link
                to="/add"
                className={`px-3 py-2 rounded-soft text-sm font-medium transition-colors ${
                  location.pathname === '/add'
                    ? 'bg-sage-100 text-sage-600'
                    : 'text-warmGray-600 hover:bg-warmGray-100'
                }`}
              >
                {t('nav.addFriend')}
              </Link>
              <Link
                to="/pricing"
                className={`px-3 py-2 rounded-soft text-sm font-medium transition-colors ${
                  location.pathname === '/pricing'
                    ? 'bg-peach-100 text-peach-500'
                    : 'text-warmGray-600 hover:bg-warmGray-100'
                }`}
              >
                {t('nav.pricing')}
              </Link>
              <LanguageSwitcher />
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-warmGray-200 mt-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 text-center text-sm text-warmGray-500">
          <p>Made with 💚 for people who care about their friendships</p>
        </div>
      </footer>
    </div>
  )
}
