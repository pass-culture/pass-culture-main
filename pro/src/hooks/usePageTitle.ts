import type { LocationListener } from 'history'
import { useEffect } from 'react'
import { matchPath, useLocation } from 'react-router-dom'

import routes, { IRoute } from 'app/AppRouter/routesMap'
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
      .reverse()
      .find(
        ({ path, parentPath }: IRoute) =>
          matchPath(`${parentPath || ''}${path}`, location.pathname) !== null
      )

    if (currentRoute?.parentPath === '/parcours-inscription') {
      document.title =
        currentRoute.path !== '/'
          ? `${currentRoute.title} - parcours d'inscription`
          : `${currentRoute.title}`
    } else {
      document.title = currentRoute
        ? `${currentRoute.title} - pass Culture Pro`
        : 'pass Culture Pro'
    }
  }, [location.pathname])
}

export default usePageTitle
