import { BrowserTracing } from '@sentry/tracing'

import pkg from '../../../package.json'
import { env } from '../environment/env'

export const sentryConfig = {
  dsn: env.SENTRY_DSN,
  integrations: [new BrowserTracing()],
  environment: env.ENV,
  tracesSampleRate: env.SAMPLE_RATE,
  release: pkg.version,
  dist: pkg.version,
}
