import { init as SentryInit } from '@sentry/browser'
import * as Sentry from '@sentry/react'
import { Integrations as TracingIntegrations } from '@sentry/tracing'
import React from 'react'
import {
  createRoutesFromChildren,
  matchRoutes,
  useLocation,
  useNavigationType,
} from 'react-router-dom'

import {
  ENVIRONMENT_NAME,
  SENTRY_SAMPLE_RATE,
  SENTRY_SERVER_URL,
} from 'utils/config'

import config from '../package.json'

export const initializeSentry = () => {
  SentryInit({
    dsn: SENTRY_SERVER_URL,
    environment: ENVIRONMENT_NAME,
    release: config.version,
    integrations: [
      new TracingIntegrations.BrowserTracing({
        routingInstrumentation: Sentry.reactRouterV6Instrumentation(
          React.useEffect,
          useLocation,
          useNavigationType,
          createRoutesFromChildren,
          matchRoutes
        ),
      }),
    ],
    tracesSampleRate: parseFloat(SENTRY_SAMPLE_RATE),
  })
}
