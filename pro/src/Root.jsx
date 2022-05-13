import { BrowserRouter, Redirect, Route, Switch } from 'react-router-dom'
import routes, { routesWithoutLayout } from 'utils/routes_map'

import AppContainer from 'app/AppContainer'
import AppLayout from 'app/AppLayout'
import FeaturedRoute from 'components/router/FeaturedRoute'
import NavigationLogger from 'components/router/NavigationLogger'
import NotFound from 'components/pages/Errors/NotFound/NotFound'
import { Provider } from 'react-redux'
import React from 'react'
import configureStore from 'store'

const { store } = configureStore()

const Root = () => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <AppContainer>
          <NavigationLogger />
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
            {routesWithoutLayout.map(route => {
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
    </Provider>
  )
}

export default Root
