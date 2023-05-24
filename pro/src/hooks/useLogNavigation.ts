import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'

import useAnalytics from './useAnalytics'

const useLogNavigation = (): void => {
  const location = useLocation()
  const { logEvent } = useAnalytics()
  const [previousPage, setPreviousPage] = useState<string>()

  useEffect(() => {
    if (logEvent) {
      logEvent?.(Events.PAGE_VIEW, { from: previousPage })
    }
    setPreviousPage(location.pathname)
    return
  }, [location, logEvent])
}

export default useLogNavigation
