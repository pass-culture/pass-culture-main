import React from 'react'
import Raven from 'raven-js'
import ReactDOM from 'react-dom'

import './utils/icon'
import 'react-dates/initialize'
import 'react-dates/lib/css/_datepicker.css'
import './styles/index.scss'
import 'typeface-barlow'

import Root from './Root'
import registerCacheWorker from './workers/cache'
import { API_URL, APP_VERSION, IS_DEV } from './utils/config'

const renderApp = () => {
  if (!IS_DEV) {
    Raven.config(`${API_URL}/client_errors`, {
      environment: process.env.NODE_ENV,
      logger: 'javascript',
      release: APP_VERSION,
    }).install()
  }
  // https://github.com/gaearon/react-hot-loader#troubleshooting
  ReactDOM.render(<Root />, document.getElementById('root'))
  registerCacheWorker()
}

// INITIALIZE THE ROOT APPLICATION
if (window.cordova) {
  document.addEventListener('deviceready', renderApp, false)
} else {
  renderApp()
}
