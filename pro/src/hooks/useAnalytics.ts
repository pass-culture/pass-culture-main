import { useContext } from 'react'

import { AnalyticsContext } from 'context/analyticsContext'

function useAnalytics() {
  return useContext(AnalyticsContext)
}

export default useAnalytics
