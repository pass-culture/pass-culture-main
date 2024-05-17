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

  return <Unavailable />
}
