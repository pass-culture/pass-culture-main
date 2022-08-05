import { matchPath, useLocation } from 'react-router'

import routes, { routesWithoutLayout } from 'routes/routes_map'

const useIsRoutePublic = (): [boolean, string] => {
  const location = useLocation()
  const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)

  const publicRouteList = [...routes, ...routesWithoutLayout].filter(
    route => route.meta && route.meta.public
  )
  const isRoutePublic = !!publicRouteList.find(route =>
    matchPath(location.pathname, route)
  )

  return [isRoutePublic, fromUrl]
}

export default useIsRoutePublic
