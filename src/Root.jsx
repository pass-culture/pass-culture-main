import React, { StrictMode } from 'react'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { BrowserRouter, Route, Switch } from 'react-router-dom'

import AppContainer from './app/AppContainer'
import FeaturedRouteContainer from './components/router/FeaturedRouteContainer'
import MatomoContainer from './components/matomo/MatomoContainer'
import NotMatch from './components/pages/not-match/NotMatch'
import browserRoutes from './components/router/browserRoutes'
import { configureStore } from './utils/store'
import Tracking from './components/tracking/Tracking'

const { store, persistor } = configureStore()

const Root = () => (
  <StrictMode>
    <Provider store={store}>
      <PersistGate
        loading={null}
        persistor={persistor}
      >
        <BrowserRouter>
          <AppContainer>
            <Switch>
              {browserRoutes.map(route => (
                <FeaturedRouteContainer
                  {...route}
                  key={route.path}
                />
              ))}
              <Route component={NotMatch} />
            </Switch>
            <MatomoContainer />
            <Tracking />
          </AppContainer>
        </BrowserRouter>
      </PersistGate>
    </Provider>
  </StrictMode>
)

export default Root
