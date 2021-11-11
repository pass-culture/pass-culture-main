import * as Sentry from '@sentry/browser'
import { Integrations as TracingIntegrations } from '@sentry/tracing'

import {
  ENVIRONMENT_NAME,
  SENTRY_SERVER_URL,
  SENTRY_SAMPLE_RATE,
  APP_VERSION,
  ANDROID_APPLICATION_ID,
} from './config'

Sentry.init({
  dsn: SENTRY_SERVER_URL,
  environment: ENVIRONMENT_NAME,
  release: APP_VERSION,
  integrations: [new TracingIntegrations.BrowserTracing()],
  tracesSampleRate: parseFloat(SENTRY_SAMPLE_RATE),
})

export const configureCustomTags = scope => {
  if (document.referrer.includes('android-app://' + ANDROID_APPLICATION_ID)) {
    scope.setTag('platform', 'application')
  } else {
    scope.setTag('platform', 'browser')
  }
}

Sentry.configureScope(configureCustomTags)
