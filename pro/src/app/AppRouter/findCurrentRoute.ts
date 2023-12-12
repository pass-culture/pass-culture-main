import { matchPath, Location } from 'react-router-dom'

import routes, { RouteConfig } from 'app/AppRouter/routesMap'
import routesIndividualOfferWizardDefinitions from 'app/AppRouter/subroutesIndividualOfferWizardMap'
import routesSignupJourneyDefinitions from 'app/AppRouter/subroutesSignupJourneyMap'
import routesSignupDefinitions from 'app/AppRouter/subroutesSignupMap'

export const findCurrentRoute = (location: Location): RouteConfig | undefined =>
  [
    ...routes,
    ...routesIndividualOfferWizardDefinitions,
    ...routesSignupDefinitions,
    ...routesSignupJourneyDefinitions,
  ]
    // This reverse is here so that subroutes (e.g. /inscription/confirmation)
    // are matched before their parents (e.g. /inscription/*)
    .reverse()
    .find(
      ({ path, parentPath }: RouteConfig) =>
        matchPath(`${parentPath || ''}${path}`, location.pathname) !== null
    )
