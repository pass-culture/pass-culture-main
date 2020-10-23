import * as Sentry from '@sentry/browser'
import { Form, Icon } from 'pass-culture-shared'
import React from 'react'
import ReactDOM from 'react-dom'
import { AppContainer } from 'react-hot-loader'
import 'typeface-barlow'

import BicInput from 'components/layout/BicInput'
import BlockContainer from 'components/layout/BlockContainer'
import IbanInput from 'components/layout/IbanInput'
import Root from 'Root'
import { ROOT_PATH, ENVIRONMENT_NAME, SENTRY_SERVER_URL } from 'utils/config'
import registerCacheWorker from 'workers/cache'

import { version } from '../package.json'
import './styles/index.scss'

// Initialize shared Icon component
Icon.rootPath = ROOT_PATH

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
  })
}

// Start app
ReactDOM.render(<Root />, document.getElementById('root'))

if (module.hot) {
  module.hot.accept('./Root', () => {
    const NextRoot = require('./Root').default
    ReactDOM.render(
      <AppContainer>
        <NextRoot />
      </AppContainer>,
      document.getElementById('root')
    )
  })
}

registerCacheWorker()
