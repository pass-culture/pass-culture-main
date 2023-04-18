import React from 'react'
import { useSelector } from 'react-redux'
import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
  useLocation,
  useMatches,
} from 'react-router-dom'

import App from 'app/App/App'
import AppLayout from 'app/AppLayout'
import { IRoute } from 'app/AppRouter/routesMap'
import useCurrentUser from 'hooks/useCurrentUser'
import NotFound from 'pages/Errors/NotFound/NotFound'
import { selectActiveFeatures } from 'store/features/selectors'
import { dehumanizedRoute } from 'utils/dehumanize'

const RouteWrapper = ({ route }: { route: IRoute }) => {
  const { currentUser } = useCurrentUser()
  const location = useLocation()
  const matches = useMatches()
  const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)
  let jsx: JSX.Element = route.element

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

  // FIXME (mageoffray, 2023-03-24)
  // This is a temporary redirection to remove humanizedId.
  // For 6 months (until around 2023-10-01) we should redirect
  // urls with humanized params to url wih non human parameters
  /* istanbul ignore next */
  if (route.meta?.shouldRedirect) {
    const newLocation = dehumanizedRoute(location, matches)
    if (location.pathname + location.search + location.hash != newLocation) {
      jsx = <Navigate to={newLocation} replace />
    }
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
