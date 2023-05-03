import type { LocationListener } from 'history'
import { useEffect } from 'react'
import { matchPath, useLocation } from 'react-router-dom'

import routes, { IRoute } from 'createReactApp/AppRouter/routesMap'
import routesOfferIndividualWizardDefinitions from 'createReactApp/AppRouter/subroutesOfferIndividualWizardMap'
import routesSignupJourneyDefinitions from 'createReactApp/AppRouter/subroutesSignupJourneyMap'
import routesSignupDefinitions from 'createReactApp/AppRouter/subroutesSignupMap'

const usePageTitle = (): LocationListener | void => {
  const location = useLocation()

  useEffect(() => {
    const currentRoute = [
      ...routes,
      ...routesOfferIndividualWizardDefinitions,
      ...routesSignupDefinitions,
      ...routesSignupJourneyDefinitions,
    ]
      .reverse()
      .find(
        ({ path, parentPath }: IRoute) =>
          matchPath(`${parentPath || ''}${path}`, location.pathname) !== null
      )

    document.title = currentRoute
      ? `${currentRoute.title} - pass Culture Pro`
      : 'pass Culture Pro'
  }, [location.pathname])
}

export default usePageTitle
