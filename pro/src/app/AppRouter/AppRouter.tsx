import React from 'react'
import { useSelector } from 'react-redux'
import { Routes, Route } from 'react-router-dom-v5-compat'

import AppLayout from 'app/AppLayout'
import routes, { routesWithoutLayout } from 'app/AppRouter/routes_map'
import NotFound from 'pages/Errors/NotFound/NotFound'
import { selectActiveFeatures } from 'store/features/selectors'

import ProtectedRoute from './ProtectedRoute'

const AppRouter = (): JSX.Element => {
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
      {activeRoutes.map(route => (
        <Route
          key={route.path}
          path={route.path}
          element={
            route.meta?.public ? (
              <AppLayout layoutConfig={route.meta && route.meta.layoutConfig}>
                <route.component />
              </AppLayout>
            ) : (
              <ProtectedRoute>
                <AppLayout layoutConfig={route.meta && route.meta.layoutConfig}>
                  <route.component />
                </AppLayout>
              </ProtectedRoute>
            )
          }
        />
      ))}

      {activeRoutesWithoutLayout.map(route => (
        <Route
          key={route.path}
          path={route.path}
          element={
            route.meta?.public ? (
              <route.component />
            ) : (
              <ProtectedRoute>
                <route.component />
              </ProtectedRoute>
            )
          }
        />
      ))}

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default AppRouter
