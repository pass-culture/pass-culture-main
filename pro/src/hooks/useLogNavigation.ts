import { useEffect } from 'react'
import { useLocation } from 'react-router-dom-v5-compat'

import { Events } from 'core/FirebaseEvents/constants'

import useAnalytics from './useAnalytics'

const useLogNavigation = (): void => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  useEffect(() => {
    if (logEvent) {
      logEvent?.(Events.PAGE_VIEW, { from: location.pathname })
    }
    return
  }, [location, logEvent])
}

export default useLogNavigation
