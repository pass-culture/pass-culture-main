import * as Sentry from '@sentry/browser'
import { Integrations as TracingIntegrations } from '@sentry/tracing'
import { Form } from 'pass-culture-shared'
import React from 'react'
import ReactDOM from 'react-dom'
import 'typeface-barlow'

import BicInput from 'components/layout/BicInput'
import BlockContainer from 'components/layout/BlockContainer'
import IbanInput from 'components/layout/IbanInput'
import Root from 'Root'
import { ENVIRONMENT_NAME, SENTRY_SERVER_URL, SENTRY_SAMPLE_RATE } from 'utils/config'

import { version } from '../package.json'
import './styles/index.scss'

import { unregister } from './registerServiceWorker'

// Initialize shared Form component
Object.assign(Form.inputsByType, {
  bic: BicInput,
  iban: IbanInput,
})

Object.assign(Form.defaultProps, {
  blockComponent: BlockContainer,
  handleFailNotification: (state, action) => {
    const {
      payload: { errors },
    } = action
    return (errors && errors[0] && errors[0].global) || 'Formulaire non validé'
  },
  handleSuccessNotification: () => 'Formulaire validé',
})

// Initialize sentry
if (SENTRY_SERVER_URL) {
  Sentry.init({
    dsn: SENTRY_SERVER_URL,
    environment: ENVIRONMENT_NAME,
    release: version,
    integrations: [new TracingIntegrations.BrowserTracing()],
    tracesSampleRate: parseFloat(SENTRY_SAMPLE_RATE),
  })
}

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
