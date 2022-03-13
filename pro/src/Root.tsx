import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter, Route, Switch, Redirect } from 'react-router-dom'

import AppContainer from 'app/AppContainer'
import AppLayout from 'app/AppLayout'
import NotFound from 'components/pages/Errors/NotFound/NotFound'
import FeaturedRoute from 'components/router/FeaturedRoute'
import NavigationLogger from 'components/router/NavigationLogger'
import { routes, routesWithMain, IRouteData, RedirectLogin } from 'routes'
import configureStore from 'store'

const { store } = configureStore()

const Root = (): JSX.Element => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <NavigationLogger />
        <AppContainer>
          <Switch>
            <Route exact path="/">
              <RedirectLogin />
            </Route>
            <Redirect
              from="/offres/:offerId([A-Z0-9]+)/edition"
              to="/offre/:offerId([A-Z0-9]+)/individuel/edition"
            />
            <Redirect
              from="/offre/:offerId([A-Z0-9]+)/scolaire/edition"
              to="/offre/:offerId([A-Z0-9]+)/collectif/edition"
            />
            {routes.map((routeData: IRouteData) => {
              return (
                <FeaturedRoute
                  exact={routeData.exact}
                  featureName={routeData.featureName}
                  key={routeData.path as string}
                  path={routeData.path}
                >
                  <AppLayout
                    layoutConfig={routeData.meta && routeData.meta.layoutConfig}
                  >
                    <routeData.component />
                  </AppLayout>
                </FeaturedRoute>
              )
            })}

            {routesWithMain.map((routeData: IRouteData) => {
              // first props, last overrides
              return (
                <FeaturedRoute
                  {...routeData}
                  exact={routeData.exact}
                  key={routeData.path as string}
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
