import * as Sentry from '@sentry/react'
import React from 'react'
import { useSelector } from 'react-redux'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import App from 'app/App/App'
import routes from 'app/AppRouter/routesMap'
import NotFound from 'pages/Errors/NotFound/NotFound'
import { selectActiveFeatures } from 'store/features/selectors'

const sentryCreateBrowserRouter =
  Sentry.wrapCreateBrowserRouter(createBrowserRouter)

const AppRouter = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)

  const activeRoutes = routes.filter(
    (route) => !route.featureName || activeFeatures.includes(route.featureName)
  )

  const router = sentryCreateBrowserRouter([
    {
      path: '/',
      element: <App />,
      children: [...activeRoutes, { path: '*', element: <NotFound /> }],
    },
  ])

  return <RouterProvider router={router} />
}

export default AppRouter
