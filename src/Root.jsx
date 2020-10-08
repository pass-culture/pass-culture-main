import React, { StrictMode } from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Route, Switch } from 'react-router-dom'
import { PersistGate } from 'redux-persist/integration/react'

import AppContainer from 'app/AppContainer'
import AppLayout from 'app/AppLayout'
import MatomoContainer from 'components/matomo/MatomoContainer'
import NoMatchPage from 'components/pages/NoMatch/NoMatch'
import FeaturedRouteContainer from 'components/router/FeaturedRouteContainer'
import configureStore from 'store'
import routes, { routesWithMain } from 'utils/routes_map'

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
            <AppContainer>
              <Switch>
                {routes.map(route => {
                  return (
                    <FeaturedRouteContainer
                      exact={route.exact}
                      key={route.path}
                      path={route.path}
                    >
                      <AppLayout layoutConfig={route.meta && route.meta.layoutConfig}>
                        <route.component />
                      </AppLayout>
                    </FeaturedRouteContainer>
                  )
                })}

                {routesWithMain.map(route => {
                  // first props, last overrides
                  return (
                    <FeaturedRouteContainer
                      {...route}
                      exact={route.exact}
                      key={route.path}
                    />
                  )
                })}
                <Route component={NoMatchPage} />
              </Switch>
              <MatomoContainer />
            </AppContainer>
          </BrowserRouter>
        </PersistGate>
      </Provider>
    </StrictMode>
  )
}

export default Root
