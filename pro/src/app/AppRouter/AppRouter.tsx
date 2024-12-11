import * as Sentry from '@sentry/react'
import { useSelector } from 'react-redux'
import { createBrowserRouter, RouterProvider } from 'react-router'

import { App } from 'app/App/App'
import { routes } from 'app/AppRouter/routesMap'
import { selectActiveFeatures } from 'commons/store/features/selectors'

import { ErrorBoundary } from './ErrorBoundary'

const sentryCreateBrowserRouter =
  Sentry.wrapCreateBrowserRouterV7(createBrowserRouter)

export const AppRouter = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)

  const activeRoutes = routes.filter(
    (route) => !route.featureName || activeFeatures.includes(route.featureName)
  )

  const router = sentryCreateBrowserRouter(
    [
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
            meta: { public: true },
          },
        ],
      },
    ],
    {
      future: {
        v7_relativeSplatPath: true,
        v7_startTransition: true,
        v7_fetcherPersist: true,
        v7_normalizeFormMethod: true,
        v7_partialHydration: true,
        v7_skipActionErrorRevalidation: true,
      },
    }
  )

  return <RouterProvider router={router} />
}
