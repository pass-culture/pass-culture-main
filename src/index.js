import React from 'react'
import ReactDOM from 'react-dom'
import { AppContainer } from 'react-hot-loader';

import './styles/index.scss'
import './utils/styles'

import Root from './Root'
// import registerCacheServiceWorker from './utils/registerCacheServiceWorker'
import registerDexieServiceWorker from './workers/dexie'

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
// registerCacheServiceWorker()
registerDexieServiceWorker()
