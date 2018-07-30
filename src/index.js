import React from 'react'
import ReactDOM from 'react-dom'
import { AppContainer } from 'react-hot-loader'

import './utils/install'

import Root from './Root'
import registerCacheWorker from './workers/cache'

const initApp = () => {
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
}

if (window.cordova) {
  document.addEventListener('deviceready', initApp, false)
} else {
  initApp()
}
