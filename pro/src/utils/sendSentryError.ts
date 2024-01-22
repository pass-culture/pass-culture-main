import * as Sentry from '@sentry/react'

export function sendSentryCustomError(
  msg: string,
  tag: 'api' | 'data-processing' = 'api',
  type: Sentry.SeverityLevel = 'error'
) {
  Sentry.withScope((scope) => {
    scope.setTag('custom-error-type', tag)
    Sentry.captureMessage(msg, type)
  })
}
