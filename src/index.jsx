import React from 'react'
import ReactDOM from 'react-dom'

import './styles/index.scss'
import 'typeface-barlow'

import Root from './Root'
import './utils/sentry'
import registerCacheWorker from './workers/cache'

const renderApp = () => {
  // https://github.com/gaearon/react-hot-loader#troubleshooting
  ReactDOM.render(<Root />, document.getElementById('root'))
  registerCacheWorker()
}

if (window.cordova) {
  document.addEventListener('deviceready', renderApp, false)
} else {
  renderApp()
}
