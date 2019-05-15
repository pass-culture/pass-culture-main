import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Route, Switch } from 'react-router-dom'
import { PersistGate } from 'redux-persist/integration/react'

import App from './App'
import NotMatchPage from './components/pages/NotMatchPage'
import routes from './utils/routes'
import { configureStore } from './utils/store'
import Matomo from './components/hocs/MatomoTracker'

const { store, persistor } = configureStore()

const Root = () => {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <BrowserRouter>
          <Matomo>
            <App>
              <Switch>
                {routes.map(route => {
                  const isExact =
                    typeof route.exact !== 'undefined' ? route.exact : true
                  // first props, last overrides
                  return <Route {...route} key={route.path} exact={isExact} />
                })}
                <Route component={NotMatchPage} />
              </Switch>
            </App>
          </Matomo>
        </BrowserRouter>
      </PersistGate>
    </Provider>
  )
}

export default Root
