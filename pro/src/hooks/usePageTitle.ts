import type { LocationListener } from 'history'
import { useEffect } from 'react'
import { matchPath, useLocation } from 'react-router-dom'

import routes, { RouteConfig } from 'app/AppRouter/routesMap'
import routesOfferIndividualWizardDefinitions from 'app/AppRouter/subroutesOfferIndividualWizardMap'
import routesSignupJourneyDefinitions from 'app/AppRouter/subroutesSignupJourneyMap'
import routesSignupDefinitions from 'app/AppRouter/subroutesSignupMap'

const usePageTitle = (): LocationListener | void => {
  const location = useLocation()

  useEffect(() => {
    const currentRoute = [
      ...routes,
      ...routesOfferIndividualWizardDefinitions,
      ...routesSignupDefinitions,
      ...routesSignupJourneyDefinitions,
    ]
      .reverse() // Albéric 09/08/2023 : I don't know why we reverse this list
      .find(
        ({ path, parentPath }: RouteConfig) =>
          matchPath(`${parentPath || ''}${path}`, location.pathname) !== null
      )

    document.title = currentRoute
      ? `${currentRoute.title} - pass Culture Pro`
      : 'pass Culture Pro'
  }, [location.pathname])
}

export default usePageTitle
