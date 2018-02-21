import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, matchPath, Redirect, Route } from 'react-router-dom'

import App from './App'
import routes from './utils/routes'
import store from './utils/store'

const Root = () => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <App>
          { routes.map((route, index) =>  <Route key={index} {...route} />) }
          {
            // and then add the route that redirects to home
            // when the path does not match anything
          }
          <Route path="/:active?"
            render={props => {
              const matchedRoute = routes.find(route =>
                matchPath(`/${props.match.params.active}`, route))
              return props.location.pathname !== '/' &&
                !matchedRoute &&
                <Redirect to='/' />
            }} />
        </App>
      </BrowserRouter>
    </Provider>
  )
}

export default Root
