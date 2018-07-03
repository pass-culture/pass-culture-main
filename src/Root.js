import React from 'react'
import { Provider } from 'react-redux'
import { matchPath, Redirect, Route, Switch } from 'react-router-dom'
import Raven from 'raven-js'

import { version } from '../package.json'
import { API_URL, IS_DEV } from './utils/config'

import 'react-dates/initialize'
import 'react-dates/lib/css/_datepicker.css'

import { ConnectedRouter } from 'react-router-redux'

import App from './App'
import routes from './utils/routes'
import store from './utils/store'
import history from './utils/history'

const Root = () => {
  if (!IS_DEV) {
    Raven
    .config(API_URL+'/client_errors', {
      release: version,
      environment: process.env.NODE_ENV,
      logger: 'javascript'})
      .install()
  }
  return (
    <Provider store={store}>
      <ConnectedRouter history={history}>
        <App>
          <Switch>
            {routes.map((route, index) => (
              <Route
                key={index}
                {...route}
                render={match => {
                  document.title =
                    (route.title ? `${route.title} - ` : '') + 'Pass Culture'
                  return route.render(match)
                }}
              />
            ))}
            <Route
              path="/:active?"
              render={props => {
                const matchedRoute = routes.find(route =>
                  matchPath(`/${props.match.params.active}`, route)
                )
                return (
                  props.location.pathname !== '/' &&
                  !matchedRoute && <Redirect to="/" />
                )
              }}
            />
          </Switch>
        </App>
      </ConnectedRouter>
    </Provider>
  )
}

export default Root
