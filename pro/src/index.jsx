import './styles/index.scss'

import { init as SentryInit } from '@sentry/browser'
import { Integrations as TracingIntegrations } from '@sentry/tracing'
import React from 'react'
import ReactDOM from 'react-dom'
import smoothscroll from 'smoothscroll-polyfill'

import Root from 'Root'
import {
  ENVIRONMENT_NAME,
  SENTRY_SAMPLE_RATE,
  SENTRY_SERVER_URL,
} from 'utils/config'

import config from '../package.json'

import { unregister } from './registerServiceWorker'

// Initialize sentry
if (SENTRY_SERVER_URL) {
  SentryInit({
    dsn: SENTRY_SERVER_URL,
    environment: ENVIRONMENT_NAME,
    release: config.version,
    integrations: [new TracingIntegrations.BrowserTracing()],
    tracesSampleRate: parseFloat(SENTRY_SAMPLE_RATE),
  })
}

smoothscroll.polyfill()

// Start app
ReactDOM.render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
  document.getElementById('root')
)

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
// reportWebVitals()

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://cra.link/PWA
unregister()
