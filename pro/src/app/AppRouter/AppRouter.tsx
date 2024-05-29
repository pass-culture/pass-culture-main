import * as Sentry from '@sentry/react'
import { useSelector } from 'react-redux'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import { App } from 'app/App/App'
import { routes } from 'app/AppRouter/routesMap'
import { selectActiveFeatures } from 'store/features/selectors'

import { ErrorBoundary } from './ErrorBoundary'

const sentryCreateBrowserRouter =
  Sentry.wrapCreateBrowserRouter(createBrowserRouter)

export const AppRouter = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)

  const activeRoutes = routes.filter(
    (route) => !route.featureName || activeFeatures.includes(route.featureName)
  )

  const router = sentryCreateBrowserRouter([
    {
      path: '/',
      element: <App />,
      errorElement: <ErrorBoundary />,
      children: [
        ...activeRoutes,
        {
          lazy: () => import('pages/Errors/NotFound/NotFound'),
          path: '*',
          title: 'Erreur 404 - Page indisponible',
        },
      ],
    },
  ])

  return <RouterProvider router={router} />
}
