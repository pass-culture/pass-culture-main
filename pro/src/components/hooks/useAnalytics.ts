import { getAnalytics } from '@firebase/analytics'
import { logEvent as analyticsLogEvent } from '@firebase/analytics'
import * as firebase from '@firebase/app'
import { useRef } from 'react'

import { firebaseConfig } from 'config/firebase'
import { Events } from 'core/FirebaseEvents/constants'

interface IUseAnalyticsReturn {
  logPageView: (page: string) => void
  logConsultCGUClick: (page: string) => void
  logPersonalDataClick: (page: string) => void
  logConsultSupportClick: (page: string) => void
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

  const logPageView = (page: string) =>
    logEvent(Events.PAGE_VIEW, { from: page })
  const logConsultCGUClick = (page: string) =>
    logEvent(Events.CLICKED_CONSULT_CGU, { from: page })
  const logPersonalDataClick = (page: string) =>
    logEvent(Events.CLICKED_PERSONAL_DATA, { from: page })
  const logConsultSupportClick = (page: string) =>
    logEvent(Events.CLICKED_CONSULT_SUPPORT, { from: page })
  return {
    logPageView,
    logConsultCGUClick,
    logPersonalDataClick,
    logConsultSupportClick,
  }
}

export default useAnalytics
