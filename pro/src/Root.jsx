import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Route, Switch, Redirect } from 'react-router-dom'
import { PersistGate } from 'redux-persist/integration/react'

import AppContainer from 'app/AppContainer'
import AppLayout from 'app/AppLayout'
import MatomoContainer from 'components/matomo/MatomoContainer'
import NotFound from 'components/pages/Errors/NotFound/NotFound'
import FeaturedRoute from 'components/router/FeaturedRoute'
import configureStore from 'store'
import routes, { routesWithMain } from 'utils/routes_map'

const { store, persistor } = configureStore()

const Root = () => {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <BrowserRouter>
          <AppContainer>
            <Switch>
              <Redirect
                from="/offres/:offerId([A-Z0-9]+)/edition"
                to="/offre/:offerId([A-Z0-9]+)/individuel/edition"
              />
              <Redirect
                from="/offre/:offerId([A-Z0-9]+)/scolaire/edition"
                to="/offre/:offerId([A-Z0-9]+)/collectif/edition"
              />
              {routes.map(route => {
                return (
                  <FeaturedRoute
                    exact={route.exact}
                    featureName={route.featureName}
                    key={route.path}
                    path={route.path}
                  >
                    <AppLayout
                      layoutConfig={route.meta && route.meta.layoutConfig}
                    >
                      <route.component />
                    </AppLayout>
                  </FeaturedRoute>
                )
              })}

              {routesWithMain.map(route => {
                // first props, last overrides
                return (
                  <FeaturedRoute
                    {...route}
                    exact={route.exact}
                    key={route.path}
                  />
                )
              })}
              <Route component={NotFound} />
            </Switch>
            <MatomoContainer />
          </AppContainer>
        </BrowserRouter>
      </PersistGate>
    </Provider>
  )
}

export default Root
