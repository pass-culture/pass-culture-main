import React, { StrictMode } from 'react'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { BrowserRouter, Route, Switch } from 'react-router-dom'

import App from './App'
import FeaturedRouteContainer from './components/router/FeaturedRouteContainer'
import Matomo from './components/matomo/Matomo'
import NotMatch from './components/pages/NotMatch'
import browserRoutes from './components/router/browserRoutes'
import { configureStore } from './utils/store'

const { store, persistor } = configureStore()

const Root = () => (
  <StrictMode>
    <Provider store={store}>
      <PersistGate
        loading={null}
        persistor={persistor}
      >
        <BrowserRouter>
          <App>
            <Switch>
              {browserRoutes.map(route => (
                <FeaturedRouteContainer
                  {...route}
                  key={route.path}
                />
              ))}
              <Route component={NotMatch} />
            </Switch>
            <Matomo />
          </App>
        </BrowserRouter>
      </PersistGate>
    </Provider>
  </StrictMode>
)

export default Root
