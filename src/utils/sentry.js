import * as Sentry from '@sentry/browser'

import { ENVIRONMENT_NAME, SENTRY_SERVER_URL_FOR_WEBAPP, APP_VERSION } from './config'

Sentry.init({
  dsn: SENTRY_SERVER_URL_FOR_WEBAPP,
  environment: ENVIRONMENT_NAME,
  release: APP_VERSION,
})
