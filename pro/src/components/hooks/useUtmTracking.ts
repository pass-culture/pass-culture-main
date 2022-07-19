import { Events } from 'core/FirebaseEvents/constants'
import { LocationListener } from 'history'
import { RootState } from 'store/reducers'
import { parse } from 'utils/query-string'
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useSelector } from 'react-redux'

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
        utm_campaign: parsedParams.utm_campaign,
        utm_medium: parsedParams.utm_medium,
        utm_source: parsedParams.utm_source,
      })
  }, [location.search])
}

export default useUtmTracking
