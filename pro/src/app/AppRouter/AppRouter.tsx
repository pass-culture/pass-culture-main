import * as Sentry from '@sentry/react'
import { useSelector } from 'react-redux'
import { createBrowserRouter, Navigate, RouterProvider } from 'react-router'

import { App } from '@/app/App/App'
import { routes } from '@/app/AppRouter/routesMap'
import { selectActiveFeatures } from '@/commons/store/features/selectors'
import { selectCurrentUser } from '@/commons/store/user/selectors'

import { ErrorBoundary } from './ErrorBoundary'
import { redirectedRoutes } from './redirectedRoutes'

const sentryCreateBrowserRouter =
  Sentry.wrapCreateBrowserRouterV7(createBrowserRouter)

export const AppRouter = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)
  const currentUser = useSelector(selectCurrentUser)
  const isUnAttached = useSelector((store: any) => store.user.isUnAttached)

  const publicRoutes = routes.filter((route) => route?.meta?.public)
  const activeRoutes = routes.filter(
    (route) =>
      !route?.meta?.public &&
      (!route.featureName || activeFeatures.includes(route.featureName))
  )

  const isUnAttachedRoute = [
    {
      lazy: () => import('@/pages/NonAttached/NonAttached'),
      path: '*',
      title: 'Rattachement en cours de traitement',
    },
  ]
  // When the user has no offerer, restrict children to ONLY the search route
  const restrictedChildren = [
    {
      element: <Navigate to="/inscription/structure/recherche" />,
      path: '/structures/:offererId/lieux/creation',
      title: 'Créer un lieu',
    },
  ]

  const normalChildren = [
    ...activeRoutes,
    ...redirectedRoutes,
    {
      lazy: () => import('@/pages/Errors/NotFound/NotFound'),
      path: '*',
      title: 'Erreur 404 - Page indisponible',
      meta: { public: true },
    },
  ]

  const children = isUnAttached
    ? isUnAttachedRoute
    : currentUser && !currentUser.hasUserOfferer
      ? restrictedChildren
      : normalChildren

  const router = sentryCreateBrowserRouter(
    [
      {
        path: '/',
        element: <App />,
        errorElement: <ErrorBoundary />,
        hydrateFallbackElement: <></>,
        children: [...publicRoutes, ...children],
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
