import * as Sentry from '@sentry/react'
import { createBrowserRouter, RouterProvider } from 'react-router'

import { App } from '@/app/App/App'
import { routes } from '@/app/AppRouter/routesMap'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectActiveFeatures } from '@/commons/store/features/selectors'
import { noop } from '@/commons/utils/noop'

import { ErrorBoundary } from './ErrorBoundary'
import { redirectedRoutes } from './redirectedRoutes'
import type { CustomRouteOrphan } from './types'

const sentryCreateBrowserRouter =
  Sentry.wrapCreateBrowserRouterV7(createBrowserRouter)

export const AppRouter = () => {
  const activeFeatures = useAppSelector(selectActiveFeatures)

  const activeRoutes = routes
    .filter(
      (route) =>
        !route.disabledWithFeatureName ||
        !activeFeatures.includes(route.disabledWithFeatureName)
    )
    .filter(
      (route) =>
        !route.featureName || activeFeatures.includes(route.featureName)
    )
  const activeRedirections = redirectedRoutes.filter(
    (route) => !route.featureName || activeFeatures.includes(route.featureName)
  )

  const router = sentryCreateBrowserRouter(
    [
      {
        path: '/',
        element: <App />,
        errorElement: <ErrorBoundary />,
        hydrateFallbackElement: <></>,
        children: [
          ...activeRedirections,
          ...activeRoutes,
          {
            lazy: () => import('@/pages/Errors/NotFound/NotFound'),
            path: '*',
            handle: {
              title: 'Erreur 404 - Page indisponible',
            },
            loader: noop,
          } satisfies CustomRouteOrphan,
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
