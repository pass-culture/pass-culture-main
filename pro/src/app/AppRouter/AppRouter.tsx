import React from 'react'
import { useSelector } from 'react-redux'
import { Redirect, Switch, useLocation } from 'react-router'
import { CompatRoute } from 'react-router-dom-v5-compat'

import AppLayout from 'app/AppLayout'
import routes, { routesWithoutLayout } from 'app/AppRouter/routes_map'
import NotFound from 'pages/Errors/NotFound/NotFound'
import { Logout } from 'pages/Logout'
import { selectActiveFeatures } from 'store/features/selectors'

import getLegacyRedirect, { ILegacyRedirect } from './utils/getLegacyRedirect'

const AppRouter = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)
  const activeRoutes = routes.filter(
    route =>
      (!route.featureName && !route.disabledFeatureName) ||
      activeFeatures.includes(route.featureName) ||
      (route.disabledFeatureName &&
        !activeFeatures.includes(route.disabledFeatureName))
  )
  const location = useLocation()
  const activeRoutesWithoutLayout = routesWithoutLayout.filter(
    route => !route.featureName || activeFeatures.includes(route.featureName)
  )

  return (
    <Switch>
      {getLegacyRedirect().map(
        ({ redirectFrom, redirectTo }: ILegacyRedirect, index: number) => (
          <Redirect
            exact
            key={`legacy-redirect-${index}`}
            from={redirectFrom}
            to={`${redirectTo}${location.search}`}
          />
        )
      )}

      <CompatRoute exact key="logout" path="/logout">
        <Logout />
      </CompatRoute>

      {activeRoutes.map(route => (
        <CompatRoute
          exact={route.exact}
          key={Array.isArray(route.path) ? route.path.join('|') : route.path}
          path={route.path}
        >
          <AppLayout layoutConfig={route.meta && route.meta.layoutConfig}>
            <route.component />
          </AppLayout>
        </CompatRoute>
      ))}
      {activeRoutesWithoutLayout.map(route => (
        <CompatRoute
          {...route}
          exact={route.exact}
          key={Array.isArray(route.path) ? route.path.join('|') : route.path}
        />
      ))}
      <CompatRoute component={NotFound} />
    </Switch>
  )
}

export default AppRouter
