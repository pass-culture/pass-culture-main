import { getAnalytics } from 'firebase/analytics'
import { logEvent as analyticsLogEvent } from 'firebase/analytics'
import { initializeApp } from 'firebase/app'

const PAGE_VIEW = 'page_view'
const CLICK_CREATE_ACCOUNT = 'createAccount'
const CLICK_ALREADY_ACCOUNT = 'alreadyHasAccount'
const CLICK_FAQ = 'hasClickedFaq'
const CLICK_HELP_CENTER = 'hasClickedHelpCenter'

const firebaseConfig = {
  apiKey: process.env.FIRBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID,
  measurementId: process.env.FIREBASE_MEASUREMENT_ID,
}

const app = initializeApp(firebaseConfig)
const analyticsProvider = getAnalytics(app)

const logEvent = (event, params = {}) => {
  console.log(event, params)
  analyticsLogEvent(analyticsProvider, event, params)
}

export const analytics = {
  logPageView: page => logEvent(PAGE_VIEW, { from: page }),
  logClickCreateAccount: () => logEvent(CLICK_CREATE_ACCOUNT),
  logClickFaq: page => logEvent(CLICK_FAQ, { page: page }),
  logClickHelpCenter: page => logEvent(CLICK_HELP_CENTER, { page: page }),
  logClickAlreayAccount: () => logEvent(CLICK_ALREADY_ACCOUNT),
}
