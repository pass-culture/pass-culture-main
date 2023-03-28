import type { LocationListener } from 'history'
import { useEffect } from 'react'
import { matchPath, useLocation } from 'react-router-dom'

import { routesDefinitions, RouteDefinition } from 'app/AppRouter/routes_map'

const usePageTitle = (): LocationListener | void => {
  const location = useLocation()

  useEffect(() => {
    // @ts-expect-error Property findLast does not exist on RouteDefinition[]
    const currentRoute = routesDefinitions.findLast(
      ({ path, parentPath }: RouteDefinition) =>
        matchPath(`${parentPath || ''}${path}`, location.pathname) !== null
    )

    document.title = currentRoute
      ? `${currentRoute.title} - pass Culture Pro`
      : 'pass Culture Pro'
  }, [location.pathname])
}

export default usePageTitle
