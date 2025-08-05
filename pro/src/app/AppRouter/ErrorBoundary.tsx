import * as Sentry from '@sentry/react'
import { Unavailable } from 'pages/Errors/Unavailable/Unavailable'
import { useEffect } from 'react'
import { useRouteError } from 'react-router'

export const ErrorBoundary = () => {
  const error = useRouteError()

  useEffect(() => {
    Sentry.captureException(error)
  }, [error])

  return <Unavailable />
}
