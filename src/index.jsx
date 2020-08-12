import React from 'react'
import ReactDOM from 'react-dom'

import './styles/index.scss'
import 'typeface-barlow'
import 'focus-visible'

import Root from './app/Root'
import './utils/sentry'
import registerCacheWorker from './workers/cache'

const renderApp = () => {
  ReactDOM.render(<Root />, document.getElementById('root'))
  registerCacheWorker()
}
renderApp()
