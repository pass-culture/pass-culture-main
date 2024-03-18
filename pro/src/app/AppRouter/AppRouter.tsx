import * as Sentry from '@sentry/react'
import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import App from 'app/App/App'
import routes from 'app/AppRouter/routesMap'
import useIsNewInterfaceActive from 'hooks/useIsNewInterfaceActive'
import { selectActiveFeatures } from 'store/features/selectors'

import { ErrorBoundary } from './ErrorBoundary'

const sentryCreateBrowserRouter =
  Sentry.wrapCreateBrowserRouter(createBrowserRouter)

const AppRouter = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)
  const isNewInterfaceActive = useIsNewInterfaceActive()

  const activeRoutes = routes.filter(
    (route) => !route.featureName || activeFeatures.includes(route.featureName)
  )

  useEffect(() => {
    document.documentElement.setAttribute(
      'data-theme',
      isNewInterfaceActive ? 'blue' : 'pink'
    )
  }, [isNewInterfaceActive])

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

export default AppRouter
