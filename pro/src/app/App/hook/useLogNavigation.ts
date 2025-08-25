import { useEffect } from 'react'
import { useLocation, useParams } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { usePrevious } from '@/commons/hooks/usePrevious'
import { isEqual } from '@/commons/utils/isEqual'
import { parseUrlParams } from '@/commons/utils/parseUrlParams'

export const useLogNavigation = (): void => {
  const location = useLocation()
  const previousLocation = usePrevious(location)
  const params = useParams()
  const { logEvent } = useAnalytics()

  useEffect(() => {
    if (
      previousLocation === undefined ||
      !isEqual(location, previousLocation)
    ) {
      const urlSearchParams = new URLSearchParams(location.search)
      const queryParams = parseUrlParams(urlSearchParams)

      const urlParams = { ...params }

      // useParams exposes a * key with the end of the path
      // when the end was not explicitely specified in the path
      // we do not want to log it
      delete urlParams['*']

      logEvent(Events.PAGE_VIEW, {
        ...urlParams,
        ...queryParams,
        from: previousLocation?.pathname,
      })
    }
  }, [location, previousLocation, params, logEvent])
}
