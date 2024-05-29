import type { LocationListener } from 'history'
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

import { findCurrentRoute } from 'app/AppRouter/findCurrentRoute'

export const usePageTitle = (): LocationListener | void => {
  const location = useLocation()

  useEffect(() => {
    const currentRoute = findCurrentRoute(location)

    document.title = currentRoute
      ? `${currentRoute.title} - pass Culture Pro`
      : 'pass Culture Pro'
  }, [location.pathname])
}
