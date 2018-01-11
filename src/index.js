import React from 'react'
import ReactDOM from 'react-dom'
import { AppContainer } from 'react-hot-loader';

import './styles/index.scss'
import './utils/styles'

import registerServiceWorker from './utils/registerServiceWorker'
import Root from './Root'

ReactDOM.render(<Root />, document.getElementById('root'))
if (module.hot) {
  module.hot.accept('./Root', () => {
    const NextRoot = require('./Root').default
    ReactDOM.render((
      <AppContainer>
        <NextRoot />
      </AppContainer>
    ), document.getElementById('root'))
  })
}
registerServiceWorker()
