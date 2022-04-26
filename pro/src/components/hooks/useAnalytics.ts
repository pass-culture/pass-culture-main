import {
  getAnalytics,
  initializeAnalytics,
  setUserId,
} from '@firebase/analytics'
import { logEvent as analyticsLogEvent } from '@firebase/analytics'
import * as firebase from '@firebase/app'
import { useRef } from 'react'

import { firebaseConfig } from 'config/firebase'
import { Events } from 'core/FirebaseEvents/constants'

export interface IUseAnalyticsReturn {
  logPageView: (page: string) => void
  logConsultCGUClick: (page: string) => void
  logPersonalDataClick: (page: string) => void
  logConsultSupportClick: (page: string) => void
  setAnalyticsUserId: (userId: string) => void
  logTutoPageView: (pageNumber: string) => void
  logForgottenPasswordClick: (page: string) => void
  logHelpCenterClick: (page: string) => void
  logCreateVenueClick: (page: string) => void
  logHomeClick: (page: string) => void
  logTicketClick: (page: string) => void
  logOfferClick: (page: string) => void
  logBookingClick: (page: string) => void
  logReimbursementClick: (page: string) => void
  logLogoutClick: (page: string) => void
  logProClick: (page: string) => void
  logCreateOfferClick: (page: string, offererId: string) => void
}

const useAnalytics = (): IUseAnalyticsReturn => {
  const app = useRef<firebase.FirebaseApp>()

  if (!app.current) {
    app.current = firebase.initializeApp(firebaseConfig)
    initializeAnalytics(app.current, {
      config: {
        send_page_view: false,
      },
    })
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
  const logHomeClick = (page: string) =>
    logEvent(Events.CLICKED_HOME, { from: page })
  const logTicketClick = (page: string) =>
    logEvent(Events.CLICKED_TICKET, { from: page })
  const logOfferClick = (page: string) =>
    logEvent(Events.CLICKED_OFFER, { from: page })
  const logBookingClick = (page: string) =>
    logEvent(Events.CLICKED_BOOKING, { from: page })
  const logReimbursementClick = (page: string) =>
    logEvent(Events.CLICKED_REIMBURSEMENT, { from: page })
  const logLogoutClick = (page: string) =>
    logEvent(Events.CLICKED_LOGOUT, { from: page })
  const logProClick = (page: string) =>
    logEvent(Events.CLICKED_PRO, { from: page })
  const logCreateVenueClick = (page: string) =>
    logEvent(Events.CLICKED_CREATE_VENUE, { from: page })
  const logCreateOfferClick = (page: string, offererId: string) =>
    logEvent(Events.CLICKED_CREATE_OFFER, { from: page, offerer_id: offererId })
  return {
    logPageView,
    logConsultCGUClick,
    logPersonalDataClick,
    logConsultSupportClick,
    setAnalyticsUserId,
    logTutoPageView,
    logForgottenPasswordClick,
    logHelpCenterClick,
    logCreateVenueClick,
    logCreateOfferClick,
    logHomeClick,
    logTicketClick,
    logOfferClick,
    logBookingClick,
    logReimbursementClick,
    logLogoutClick,
    logProClick,
  }
}

export default useAnalytics
