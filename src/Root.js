import React from 'react'
import has from 'lodash.has'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { BrowserRouter, Route, Switch } from 'react-router-dom'

import App from './App'
import routes from './utils/routes'
import { configureStore } from './utils/store'
import NotMatch from './components/pages/NotMatch'

const { store, persistor } = configureStore()

const Root = () => (
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <BrowserRouter>
        <App>
          <Switch>
            {routes.map(route => {
              const hasExact = has(route, 'exact')
              const isexact = hasExact ? route.exact : true
              // first props, last overrides
              return <Route {...route} key={route.path} exact={isexact} />
            })}
            <Route component={NotMatch} />
          </Switch>
        </App>
      </BrowserRouter>
    </PersistGate>
  </Provider>
)

export default Root
