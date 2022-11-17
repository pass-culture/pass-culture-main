import React, { useEffect } from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'

interface ILogRouteNavigationProps {
  route: { title?: string; hasSubRoutes?: boolean }
  children: React.ReactNode | React.ReactNode[]
}
const LogRouteNavigation = ({
  route,
  children,
}: ILogRouteNavigationProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  useEffect(() => {
    if (logEvent !== null && !route.hasSubRoutes) {
      const fromTitle = document.title
      document.title = `${route.title} - pass Culture Pro`
      logEvent(Events.PAGE_VIEW, {
        from: fromTitle,
        title: document.title,
      })
    }
  }, [route.title, logEvent])

  return <>{children}</>
}

export default LogRouteNavigation
