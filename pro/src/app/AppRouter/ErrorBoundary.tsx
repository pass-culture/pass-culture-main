import * as Sentry from '@sentry/react'
import { useEffect } from 'react'
import { useRouteError } from 'react-router'

import { Unavailable } from '@/pages/Errors/Unavailable/Unavailable'

export const ErrorBoundary = () => {
  const error = useRouteError()

  useEffect(() => {
    Sentry.captureException(error)
  }, [error])

  return <Unavailable />
}
