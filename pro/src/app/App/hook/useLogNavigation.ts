import { useEffect, useState } from 'react'
import { useLocation, useParams } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'

export const useLogNavigation = (): void => {
  const location = useLocation()
  const params = useParams()
  const { logEvent } = useAnalytics()
  const [previousPage, setPreviousPage] = useState<string>()

  useEffect(() => {
    const queryParams = Object.fromEntries(new URLSearchParams(location.search))
    const urlParams = { ...params }

    // useParams exposes a * key with the end of the path
    // when the end was not explicitely specified in the path
    // we do not want to log it
    delete urlParams['*']

    logEvent(Events.PAGE_VIEW, {
      ...urlParams,
      ...queryParams,
      from: previousPage,
    })
    setPreviousPage(location.pathname)

    return
  }, [location, logEvent])
}
