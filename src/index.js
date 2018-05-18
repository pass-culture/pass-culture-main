import React from 'react'
import ReactDOM from 'react-dom'
import { AppContainer } from 'react-hot-loader'

import './styles/index.scss'
import 'typeface-barlow'

import Root from './Root'
import store from './utils/store'
import registerCacheWorker from './workers/cache'
import registerDexieWorker from './workers/dexie/register'


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
  registerDexieWorker(store)
}

if (window.cordova) {
  document.addEventListener("deviceready", initApp, false);
} else {
  initApp();
}
