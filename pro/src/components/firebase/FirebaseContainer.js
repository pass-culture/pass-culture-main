import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

import { analytics } from 'utils/firebase'

const FirebaseAnalytics = () => {
  let location = useLocation()
  useEffect(() => {
    analytics.logPageView(location.pathname)
  }, [location])
  return null
}

export default FirebaseAnalytics
