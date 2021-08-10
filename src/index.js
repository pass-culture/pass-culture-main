import { init as SentryInit } from '@sentry/browser'
import { Integrations as TracingIntegrations } from '@sentry/tracing'
import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'

import { ENVIRONMENT_NAME, SENTRY_SERVER_URL, SENTRY_SAMPLE_RATE } from 'utils/config'

import { version } from '../package.json'

import App from './App'

// Initialize sentry
if (SENTRY_SERVER_URL) {
  SentryInit({
    dsn: SENTRY_SERVER_URL,
    environment: ENVIRONMENT_NAME,
    release: version,
    integrations: [new TracingIntegrations.BrowserTracing()],
    tracesSampleRate: parseFloat(SENTRY_SAMPLE_RATE),
  })
}

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
)
