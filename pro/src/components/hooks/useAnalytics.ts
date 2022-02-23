import { getAnalytics } from '@firebase/analytics'
import { logEvent as analyticsLogEvent } from '@firebase/analytics'
import * as firebase from '@firebase/app'
import { useRef } from 'react'

import { firebaseConfig } from 'config/firebase'
import { PAGE_VIEW } from 'core/FirebaseEvents/constants'

interface IUseAnalyticsReturn {
  logPageView: (page: string) => void
}

const useAnalytics = (): IUseAnalyticsReturn => {
  const app = useRef<firebase.FirebaseApp>()

  if (!app.current) {
    app.current = firebase.initializeApp(firebaseConfig)
  }

  const analyticsProvider = getAnalytics(app.current)
  const logEvent = (event: string, params: { [key: string]: string } = {}) => {
    analyticsLogEvent(analyticsProvider, event, params)
  }

  const logPageView = (page: string) => logEvent(PAGE_VIEW, { from: page })

  return {
    logPageView,
  }
}

export default useAnalytics
