import React from 'react'
import { Provider } from 'react-redux'
import { matchPath, Redirect, Route, Switch } from 'react-router-dom'

import { ConnectedRouter } from 'react-router-redux'

import App from './App'
import routes from './utils/routes'
import store from './utils/store'
import history from './utils/history'

const Root = () => {
  return (
    <Provider store={store}>
      <ConnectedRouter history={history}>
        <App>
          <Switch>
            { routes.map((route, index) =>  (
              <Route key={index} {...route} render={(match) => {
                document.title = (route.title ? `${route.title} - ` : '') + 'Pass Culture';
                return route.render(match);
              }} />
            ))}
            <Route path="/:active?"
              render={props => {
                const matchedRoute = routes.find(route =>
                  matchPath(`/${props.match.params.active}`, route))
                return props.location.pathname !== '/' && !matchedRoute && <Redirect to='/' />
              }} />
          </Switch>
        </App>
      </ConnectedRouter>
    </Provider>
  )
}

export default Root
