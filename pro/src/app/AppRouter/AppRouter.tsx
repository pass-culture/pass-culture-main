import React from 'react'
import { useSelector } from 'react-redux'
import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
  useLocation,
} from 'react-router-dom'

import App from 'app/App/App'
import AppLayout from 'app/AppLayout'
import { IRoute } from 'app/AppRouter/routes_map'
import useCurrentUser from 'hooks/useCurrentUser'
import NotFound from 'pages/Errors/NotFound/NotFound'
import { selectActiveFeatures } from 'store/features/selectors'

const RouteWrapper = ({ route }: { route: IRoute }) => {
  const { currentUser } = useCurrentUser()
  const location = useLocation()
  const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)
  let jsx = <route.element />

  if (!route.meta?.withoutLayout) {
    jsx = (
      <AppLayout layoutConfig={route.meta && route.meta.layoutConfig}>
        {jsx}
      </AppLayout>
    )
  }

  if (!route.meta?.public && currentUser === null) {
    const loginUrl = fromUrl.includes('logout')
      ? '/connexion'
      : `/connexion?de=${fromUrl}`

    jsx = <Navigate to={loginUrl} replace />
  }

  return <App>{jsx}</App>
}

const AppRouter = ({ routes }: { routes: IRoute[] }): JSX.Element => {
  const activeFeatures = useSelector(selectActiveFeatures)

  const activeRoutes = routes
    .filter(
      route => !route.featureName || activeFeatures.includes(route.featureName)
    )
    .map(route => ({
      ...route,
      element: <RouteWrapper route={route} />,
    }))

  const router = createBrowserRouter([
    ...activeRoutes,
    { path: '*', element: <NotFound /> },
  ])

  return <RouterProvider router={router} />
}

export default AppRouter
