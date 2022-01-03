import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Route, Switch } from 'react-router-dom'
import { PersistGate } from 'redux-persist/integration/react'

import AppContainer from 'app/AppContainer'
import AppLayout from 'app/AppLayout'
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
          </AppContainer>
        </BrowserRouter>
      </PersistGate>
    </Provider>
  )
}

export default Root
