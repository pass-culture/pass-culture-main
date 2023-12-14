import { matchPath, Location } from 'react-router-dom'

import routes, { RouteConfig } from 'app/AppRouter/routesMap'
import { routesIndividualOfferWizard } from 'app/AppRouter/subroutesIndividualOfferWizardMap'
import { routesSignupJourney } from 'app/AppRouter/subroutesSignupJourneyMap'
import { routesSignup } from 'app/AppRouter/subroutesSignupMap'

export const findCurrentRoute = (location: Location): RouteConfig | undefined =>
  [
    ...routes,
    ...routesIndividualOfferWizard,
    ...routesSignup,
    ...routesSignupJourney,
  ]
    // This reverse is here so that subroutes (e.g. /inscription/confirmation)
    // are matched before their parents (e.g. /inscription/*)
    .reverse()
    .find(
      ({ path, parentPath }: RouteConfig) =>
        matchPath(`${parentPath || ''}${path}`, location.pathname) !== null
    )
