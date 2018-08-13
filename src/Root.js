import Raven from 'raven-js'
import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Route, Switch } from 'react-router-dom'
import { PersistGate } from 'redux-persist/integration/react'

import App from './App'
import persistor from './utils/persistor'
import routes from './utils/routes'
import store from './utils/store'
import { API_URL, IS_DEV } from './utils/config'
import { ownProperty } from './helpers'
import { version } from '../package.json'
import NotMatch from './components/pages/NotMatch'

const buildRoute = route => {
  // lodash.get retourne 'null' pour une valeur 'null'
  const hasexact = ownProperty(route, 'exact')
  const isexact = hasexact ? route.exact : true
  // first props, last overrides
  return <Route {...route} key={route.path} exact={isexact} />
}

const Root = () => {
  if (!IS_DEV) {
    Raven.config(`${API_URL}/client_errors`, {
      environment: process.env.NODE_ENV,
      logger: 'javascript',
      release: version,
    }).install()
  }
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <BrowserRouter>
          <App>
            <Switch>
              {routes.map(buildRoute)}
              <Route component={NotMatch} />
            </Switch>
          </App>
        </BrowserRouter>
      </PersistGate>
    </Provider>
  )
}

export default Root
