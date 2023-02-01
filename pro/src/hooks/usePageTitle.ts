import type { LocationListener } from 'history'
import { useEffect } from 'react'
import { matchPath, useLocation } from 'react-router-dom'

import routes, {
  IRoute,
  routeNotFound,
  routesWithoutLayout,
  subRoutesOfferIndividualWizard,
  subRoutesInscription,
  subRoutesCollectiveOfferEdition,
  subRoutesCollectiveOfferEdition2,
} from 'app/AppRouter/routes_map'
import { Events } from 'core/FirebaseEvents/constants'

import useAnalytics from './useAnalytics'

const usePageTitle = (): LocationListener | void => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  useEffect(() => {
    const currentRoute = [
      ...subRoutesCollectiveOfferEdition2,
      ...subRoutesCollectiveOfferEdition,
      ...subRoutesInscription,
      ...subRoutesOfferIndividualWizard,
      ...routes,
      ...routesWithoutLayout,
      routeNotFound,
    ].find(
      (route: Partial<IRoute>) => matchPath(location.pathname, route) !== null
    )

    document.title = currentRoute
      ? `${currentRoute.title} - pass Culture Pro`
      : 'pass Culture Pro'

    logEvent?.(Events.PAGE_VIEW, {
      from: location.pathname,
    })
  }, [location.pathname])
}

export default usePageTitle
