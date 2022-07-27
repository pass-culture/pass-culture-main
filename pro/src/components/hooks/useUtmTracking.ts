import type { LocationListener } from 'history'
import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import { RootState } from 'store/reducers'
import { parse } from 'utils/query-string'

const useUtmTracking = (): LocationListener | void => {
  const location = useLocation()
  const logEvent = useSelector((state: RootState) => state.app.logEvent)
  useEffect(() => {
    const parsedParams = parse(location.search)
    if (
      'utm_campaign' in parsedParams &&
      'utm_medium' in parsedParams &&
      'utm_source' in parsedParams
    )
      logEvent(Events.UTM_TRACKING_CAMPAIGN, {
        traffic_campaign: parsedParams.utm_campaign,
        traffic_medium: parsedParams.utm_medium,
        traffic_source: parsedParams.utm_source,
      })
  }, [location.search])
}

export default useUtmTracking
