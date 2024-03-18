import * as Sentry from '@sentry/react'
import { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import App from 'app/App/App'
import routes from 'app/AppRouter/routesMap'
import { selectActiveFeatures } from 'store/features/selectors'
import Toggle from 'ui-kit/Toggle'

import { ErrorBoundary } from './ErrorBoundary'

const sentryCreateBrowserRouter =
  Sentry.wrapCreateBrowserRouter(createBrowserRouter)

const AppRouter = (): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)

  const activeRoutes = routes.filter(
    (route) => !route.featureName || activeFeatures.includes(route.featureName)
  )
  const [theme, setTheme] = useState('old')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

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

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'old' ? 'new' : 'old'))
  }

  return (
    <>
      <Toggle label={theme} handleClick={() => toggleTheme()} />
      <RouterProvider router={router} />
    </>
  )
}

export default AppRouter
