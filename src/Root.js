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

const Root = () => {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <BrowserRouter>
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
        </BrowserRouter>
      </PersistGate>
    </Provider>
  )
}

export default Root
