// eslint-disable-next-line import/named
import { Location, LocationListener } from 'history'
import { useEffect } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'

const useLogNavigation = (): LocationListener | void => {
  const analytics = useAnalytics()
  const history = useHistory()
  const location = useLocation()
  useEffect(() => {
    const unlisten = history.listen((nextLocation: Location) => {
      if (location.pathname !== nextLocation.pathname) {
        analytics.logPageView(nextLocation.pathname)
      }
    })
    return unlisten
  })
}

export default useLogNavigation
