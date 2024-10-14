import * as Sentry from '@sentry/react'

export function sendSentryCustomError(
  error: unknown, // error are typed as unknown in catch blocks
  extraData?: Record<string, unknown>,
  tag: 'api' | 'data-processing' | (string & NonNullable<unknown>) = 'api'
) {
  Sentry.withScope((scope) => {
    scope.setTag('custom-error-type', tag)

    if (extraData !== undefined) {
      Sentry.addBreadcrumb({
        message: 'Additional error data',
        level: 'info',
        data: extraData,
      })
    }
    Sentry.captureException(error)
  })
}
