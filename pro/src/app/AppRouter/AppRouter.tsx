import * as Sentry from '@sentry/react'
import { createBrowserRouter, RouterProvider } from 'react-router'

import { App } from '@/app/App/App'
import { routes } from '@/app/AppRouter/routesMap'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectActiveFeatures } from '@/commons/store/features/selectors'

import { AppRouterGuard } from './AppRouterGuard'
import { ErrorBoundary } from './ErrorBoundary'
import { redirectedRoutes } from './redirectedRoutes'

const sentryCreateBrowserRouter =
  Sentry.wrapCreateBrowserRouterV7(createBrowserRouter)

export const AppRouter = (): JSX.Element => {
  const activeFeatures = useAppSelector(selectActiveFeatures)
  const withSwitchVenueFeature = activeFeatures.includes('WIP_SWITCH_VENUE')

  const activeRoutes = routes.filter(
    (route) => !route.featureName || activeFeatures.includes(route.featureName)
  )
  const activeRedirections = redirectedRoutes.filter(
    (route) => !route.featureName || activeFeatures.includes(route.featureName)
  )

  const router = sentryCreateBrowserRouter(
    [
      {
        path: '/',
        element: withSwitchVenueFeature ? (
          <App />
        ) : (
          <AppRouterGuard>
            <App />
          </AppRouterGuard>
        ),
        errorElement: <ErrorBoundary />,
        hydrateFallbackElement: <></>,
        children: [
          ...activeRedirections,
          ...activeRoutes,
          {
            lazy: () => import('@/pages/Errors/NotFound/NotFound'),
            path: '*',
            title: 'Erreur 404 - Page indisponible',
            meta: { public: true, canBeLoggedIn: true },
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
