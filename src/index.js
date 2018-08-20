import React from 'react'
import ReactDOM from 'react-dom'

import './utils/install'
import Root from './Root'
import registerCacheWorker from './workers/cache'

const renderApp = () => {
  ReactDOM.render(<Root />, document.getElementById('root'))
  registerCacheWorker()
}

if (window.cordova) {
  document.addEventListener('deviceready', renderApp, false)
} else {
  renderApp()
}
