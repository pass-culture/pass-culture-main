import * as Sentry from '@sentry/react'
import React, { useEffect } from 'react'
import { useRouteError } from 'react-router-dom'

import { Unavailable } from 'pages/Errors/Unavailable/Unavailable'

export const ErrorBoundary = () => {
  const error = useRouteError()

  useEffect(() => {
    Sentry.captureException(error)
  }, [error])

  return <Unavailable />
}
