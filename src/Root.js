import Raven from 'raven-js'
import React from 'react'
import { Provider } from 'react-redux'
import {
  BrowserRouter,
  matchPath,
  Redirect,
  Route,
  Switch,
} from 'react-router-dom'
import { PersistGate } from 'redux-persist/integration/react'

import App from './App'
import persistor from './utils/persistor'
import routes from './utils/routes'
import store from './utils/store'
import { API_URL, IS_DEV } from './utils/config'
import { version } from '../package.json'

const buildRoute = route => (
  <Route
    key={route.path}
    exact={!route.subroutes}
    component={route.component}
  />
)

const buildNotFoundRoute = () => (
  <Route
    path="/:active?"
    render={({ match, location }) => {
      const { active } = match.params
      const matchedRoute = routes.find(route => matchPath(`/${active}`, route))
      return location.pathname !== '/' && !matchedRoute && <Redirect to="/" />
    }}
  />
)

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
              {buildNotFoundRoute()}
            </Switch>
          </App>
        </BrowserRouter>
      </PersistGate>
    </Provider>
  )
}

export default Root
