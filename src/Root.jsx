import React, { StrictMode } from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Route, Switch } from 'react-router-dom'
import { PersistGate } from 'redux-persist/integration/react'

import App from './App'
import NotMatchPage from './components/pages/NotMatchPage'
import routes from './utils/routes'
import configureStore from './utils/store'
import MatomoPageTracker from './components/matomo/MatomoPageTracker'

const { store, persistor } = configureStore()

const Root = () => {
  return (
    <StrictMode>
      <Provider store={store}>
        <PersistGate
          loading={null}
          persistor={persistor}
        >
          <BrowserRouter>
            <App>
              <Switch>
                {routes.map(route => {
                  const isExact = typeof route.exact !== 'undefined' ? route.exact : true
                  // first props, last overrides
                  return (<Route
                    {...route}
                    exact={isExact}
                    key={route.path}
                          />)
                })}
                <Route component={NotMatchPage} />
              </Switch>
              <MatomoPageTracker />
            </App>
          </BrowserRouter>
        </PersistGate>
      </Provider>
    </StrictMode>
  )
}

export default Root
