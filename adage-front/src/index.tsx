import { init as SentryInit } from '@sentry/browser'
import { Integrations as TracingIntegrations } from '@sentry/tracing'
import * as React from 'react'
import * as ReactDOM from 'react-dom'
import './index.scss'

import {
  AlgoliaQueryContextProvider,
  FiltersContextProvider,
  FacetFiltersContextProvider,
} from 'app/providers'
import { FeaturesContextProvider } from 'app/providers/FeaturesContextProvider'
import {
  ENVIRONMENT_NAME,
  SENTRY_SERVER_URL,
  SENTRY_SAMPLE_RATE,
} from 'utils/config'

import { version } from '../package.json'

import { App } from './app/App'

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
    <FeaturesContextProvider>
      <FiltersContextProvider>
        <AlgoliaQueryContextProvider>
          <FacetFiltersContextProvider>
            <App />
          </FacetFiltersContextProvider>
        </AlgoliaQueryContextProvider>
      </FiltersContextProvider>
    </FeaturesContextProvider>
  </React.StrictMode>,
  document.getElementById('root')
)
