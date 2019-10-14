import * as Sentry from '@sentry/browser'

import { ENVIRONMENT_NAME, SENTRY_SERVER_URL, APP_VERSION } from './config'

const initSentry = () => {
  Sentry.init({
    dsn: SENTRY_SERVER_URL,
    environment: ENVIRONMENT_NAME,
    release: APP_VERSION,
  })
}

export default initSentry
