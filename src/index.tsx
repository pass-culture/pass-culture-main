import { init as SentryInit } from "@sentry/browser"
import { Integrations as TracingIntegrations } from "@sentry/tracing"
import * as React from "react"
import * as ReactDOM from "react-dom"
import "./index.scss"

import {
  REACT_APP_ENVIRONMENT_NAME,
  REACT_APP_SENTRY_SERVER_URL,
  REACT_APP_SENTRY_SAMPLE_RATE,
} from "utils/config"

import { version } from "../package.json"

import App from "./app/App"

// Initialize sentry
if (REACT_APP_SENTRY_SERVER_URL) {
  SentryInit({
    dsn: REACT_APP_SENTRY_SERVER_URL,
    environment: REACT_APP_ENVIRONMENT_NAME,
    release: version,
    integrations: [new TracingIntegrations.BrowserTracing()],
    tracesSampleRate: parseFloat(REACT_APP_SENTRY_SAMPLE_RATE),
  })
}

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById("root")
)
