import React from 'react'
import { useSelector } from 'react-redux'
import { createBrowserRouter, RouterProvider } from 'react-router-dom-v5-compat'

import App from 'app/App/App'
import AppLayout from 'app/AppLayout'
import routes, { IRoute, routesWithoutLayout } from 'app/AppRouter/routes_map'
import NotFound from 'pages/Errors/NotFound/NotFound'
import { selectActiveFeatures } from 'store/features/selectors'

import ProtectedRoute from './ProtectedRoute'

const renderRouteComponent = (route: IRoute, withLayout: boolean) => {
  let jsx = <route.element />

  if (!route.meta?.public) {
    jsx = <ProtectedRoute>{jsx}</ProtectedRoute>
  }

  if (withLayout) {
    jsx = (
      <AppLayout layoutConfig={route.meta && route.meta.layoutConfig}>
        {jsx}
      </AppLayout>
    )
  }

  return <App>{jsx}</App>
}

const AppRouter = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)

  const activeRoutes = routes
    .filter(
      route => !route.featureName || activeFeatures.includes(route.featureName)
    )
    .map(route => ({ ...route, element: renderRouteComponent(route, true) }))

  const activeRoutesWithoutLayout = routesWithoutLayout
    .filter(
      route => !route.featureName || activeFeatures.includes(route.featureName)
    )
    .map(route => ({ ...route, element: renderRouteComponent(route, false) }))

  const router = createBrowserRouter([
    ...activeRoutes,
    ...activeRoutesWithoutLayout,
    { path: '*', element: <NotFound /> },
  ])

  return <RouterProvider router={router} />
}

export default AppRouter
