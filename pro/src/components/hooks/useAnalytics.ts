import { getAnalytics, setUserId } from '@firebase/analytics'
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
  setAnalyticsUserId: (userId: string) => void
  logTutoPageView: (pageNumber: string) => void
  logForgottenPasswordClick: (page: string) => void
  logHelpCenterClick: (page: string) => void
}

const useAnalytics = (): IUseAnalyticsReturn => {
  const app = useRef<firebase.FirebaseApp>()

  if (!app.current) {
    app.current = firebase.initializeApp(firebaseConfig)
  }

  const analyticsProvider = getAnalytics(app.current)
  const setAnalyticsUserId = (userId: string) => {
    setUserId(analyticsProvider, userId)
  }
  const logEvent = (event: string, params: { [key: string]: string } = {}) => {
    analyticsLogEvent(analyticsProvider, event, params)
  }

  const logPageView = (page: string) =>
    logEvent(Events.PAGE_VIEW, { from: page })
  const logTutoPageView = (pageNumber: string) =>
    logEvent(Events.TUTO_PAGE_VIEW, { page_number: pageNumber })
  const logConsultCGUClick = (page: string) =>
    logEvent(Events.CLICKED_CONSULT_CGU, { from: page })
  const logPersonalDataClick = (page: string) =>
    logEvent(Events.CLICKED_PERSONAL_DATA, { from: page })
  const logConsultSupportClick = (page: string) =>
    logEvent(Events.CLICKED_CONSULT_SUPPORT, { from: page })
  const logForgottenPasswordClick = (page: string) =>
    logEvent(Events.CLICKED_FORGOTTEN_PASSWORD, { from: page })
  const logHelpCenterClick = (page: string) =>
    logEvent(Events.CLICKED_HELP_CENTER, { from: page })
  return {
    logPageView,
    logConsultCGUClick,
    logPersonalDataClick,
    logConsultSupportClick,
    setAnalyticsUserId,
    logTutoPageView,
    logForgottenPasswordClick,
    logHelpCenterClick,
  }
}

export default useAnalytics
