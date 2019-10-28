import * as Sentry from '@sentry/browser'

import { ENVIRONMENT_NAME, SENTRY_SERVER_URL_FOR_PRO } from './config'
import { version } from '../../package.json'

Sentry.init({
  dsn: SENTRY_SERVER_URL_FOR_PRO,
  environment: ENVIRONMENT_NAME,
  release: version,
})
