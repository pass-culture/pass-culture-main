import { matchPath, Location } from 'react-router-dom'

import { RouteConfig, routes } from 'app/AppRouter/routesMap'
import { routesIndividualOfferWizard } from 'app/AppRouter/subroutesIndividualOfferWizardMap'
import { routesSignupJourney } from 'app/AppRouter/subroutesSignupJourneyMap'
import { routesSignup } from 'app/AppRouter/subroutesSignupMap'
import { routesVenueEdition } from 'pages/VenueEdition/subroutesVenueEdition'

import { routesReimbursements } from './subroutesReimbursements'

export const findCurrentRoute = (location: Location): RouteConfig | undefined =>
  [
    ...routes,
    ...routesIndividualOfferWizard,
    ...routesSignup,
    ...routesSignupJourney,
    ...routesReimbursements,
    ...routesVenueEdition,
  ]
    // This reverse is here so that subroutes (e.g. /inscription/confirmation)
    // are matched before their parents (e.g. /inscription/*)
    .reverse()
    .find(
      ({ path }: RouteConfig) => matchPath(path, location.pathname) !== null
    )
