import * as Sentry from '@sentry/react'
import React, { useEffect } from 'react'
import { useRouteError } from 'react-router-dom'

import { isError } from 'apiClient/helpers'
import { Unavailable } from 'pages/Errors/Unavailable/Unavailable'

const isDynamicImportError = (error: unknown) =>
  isError(error) && error.message.includes('dynamically imported module')

export const ErrorBoundary = () => {
  const error = useRouteError()

  useEffect(() => {
    if (isDynamicImportError(error)) {
      return
    }
    Sentry.captureException(error)
  }, [error])

  if (isDynamicImportError(error)) {
    // Reload page when a dynamic import fails (when we release a new version)
    // https://github.com/remix-run/react-router/discussions/10333
    // Error message is different in some browsers:
    // Chrome: Failed to fetch dynamically imported module
    // Firefox/Safari: error loading dynamically imported module)
    window.location.reload()

    return
  }

  return <Unavailable />
}
