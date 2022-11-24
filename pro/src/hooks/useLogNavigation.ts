import type { LocationListener } from 'history'
import { useEffect } from 'react'
import { matchPath, useLocation } from 'react-router-dom'

import routes, { IRoute, routesWithoutLayout } from 'app/AppRouter/routes_map'
import { Events } from 'core/FirebaseEvents/constants'

import useAnalytics from './useAnalytics'

const useLogNavigation = (): LocationListener | void => {
  const location = useLocation()
  const { logEvent } = useAnalytics()
  useEffect(() => {
    if (logEvent) {
      logEvent?.(Events.PAGE_VIEW, { from: location.pathname })
    }
  }, [logEvent])

  useEffect(() => {
    const currentRoute = [...routes, ...routesWithoutLayout].find(
      (route: IRoute) => matchPath(location.pathname, route)
    )
    if (currentRoute) {
      const fromTitle = document.title
      document.title = currentRoute.title || 'pass Culture Pro'
      logEvent?.(Events.PAGE_VIEW, { from: fromTitle, title: document.title })
    }
  }, [location.pathname])
}

export default useLogNavigation
