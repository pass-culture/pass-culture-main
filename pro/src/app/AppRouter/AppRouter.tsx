import React from 'react'
import { useSelector } from 'react-redux'
import { Redirect, Switch, useLocation, Route } from 'react-router'
import { Routes, Route as RouteV6 } from 'react-router-dom-v5-compat'

import AppLayout from 'app/AppLayout'
import routes, { routesWithoutLayout } from 'app/AppRouter/routes_map'
import NotFound from 'pages/Errors/NotFound/NotFound'
import { Logout } from 'pages/Logout'
import { selectActiveFeatures } from 'store/features/selectors'

import getLegacyRedirect, { ILegacyRedirect } from './utils/getLegacyRedirect'

const AppRouterV6 = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)
  const activeRoutes = routes.filter(
    route =>
      (!route.featureName && !route.disabledFeatureName) ||
      activeFeatures.includes(route.featureName) ||
      (route.disabledFeatureName &&
        !activeFeatures.includes(route.disabledFeatureName))
  )
  const activeRoutesWithoutLayout = routesWithoutLayout.filter(
    route => !route.featureName || activeFeatures.includes(route.featureName)
  )

  return (
    <Routes>
      {activeRoutes
        .filter(route => route.useV6Router)
        .map(route =>
          Array.isArray(route.path) ? (
            route.path.map(path => (
              <RouteV6
                key={path}
                path={path}
                element={
                  <AppLayout
                    layoutConfig={route.meta && route.meta.layoutConfig}
                  >
                    <route.component />
                  </AppLayout>
                }
              />
            ))
          ) : (
            <RouteV6
              key={route.path}
              path={route.path}
              element={
                <AppLayout layoutConfig={route.meta && route.meta.layoutConfig}>
                  <route.component />
                </AppLayout>
              }
            />
          )
        )}

      {activeRoutesWithoutLayout
        .filter(route => route.useV6Router)
        .map(route =>
          Array.isArray(route.path) ? (
            route.path.map(path => (
              <RouteV6 key={path} path={path} element={<route.component />} />
            ))
          ) : (
            <RouteV6
              key={route.path}
              path={route.path}
              element={<route.component />}
            />
          )
        )}

      <RouteV6 path="*" element={<NotFound />} />
    </Routes>
  )
}

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
    <>
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

        <Route exact key="logout" path="/logout">
          <Logout />
        </Route>

        {activeRoutes
          .filter(route => !route.useV6Router)
          .map(route => (
            <Route
              exact={route.exact}
              key={
                Array.isArray(route.path) ? route.path.join('|') : route.path
              }
              path={route.path}
            >
              <AppLayout layoutConfig={route.meta && route.meta.layoutConfig}>
                <route.component />
              </AppLayout>
            </Route>
          ))}

        {activeRoutesWithoutLayout
          .filter(route => !route.useV6Router)
          .map(route => (
            <Route
              {...route}
              exact={route.exact}
              key={
                Array.isArray(route.path) ? route.path.join('|') : route.path
              }
            />
          ))}

        <Route exact={false} component={AppRouterV6} />
      </Switch>
    </>
  )
}

export default AppRouter
