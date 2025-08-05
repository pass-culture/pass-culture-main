import { findCurrentRoute } from 'app/AppRouter/findCurrentRoute'
import { useEffect } from 'react'
import { useLocation } from 'react-router'

export const usePageTitle = () => {
  const location = useLocation()

  useEffect(() => {
    const currentRoute = findCurrentRoute(location)

    document.title = currentRoute
      ? `${currentRoute.title} - pass Culture Pro`
      : 'pass Culture Pro'

    const pageTitleAnnouncer = document.getElementById('page-title-announcer')
    if (pageTitleAnnouncer) {
      pageTitleAnnouncer.textContent = currentRoute?.title || 'pass Culture Pro'
    }
  }, [location])
}
