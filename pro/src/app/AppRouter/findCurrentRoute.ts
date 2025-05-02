import { matchPath, Location } from 'react-router'

import { RouteConfig, routes } from 'app/AppRouter/routesMap'
import {
  routesIndividualOfferWizard,
  routesOnboardingIndividualOfferWizard,
} from 'app/AppRouter/subroutesIndividualOfferWizardMap'
import { routesSignupJourney } from 'app/AppRouter/subroutesSignupJourneyMap'
import { routesSignup } from 'app/AppRouter/subroutesSignupMap'

import { routesReimbursements } from './subroutesReimbursements'

export const findCurrentRoute = (location: Location): RouteConfig | undefined =>
  [
    ...routes,
    ...routesIndividualOfferWizard,
    ...routesOnboardingIndividualOfferWizard,
    ...routesSignup,
    ...routesSignupJourney,
    ...routesReimbursements,
  ]
    // This reverse is here so that subroutes (e.g. /inscription/confirmation)
    // are matched before their parents (e.g. /inscription/*)
    .reverse()
    .find(
      ({ path }: RouteConfig) => matchPath(path, location.pathname) !== null
    )
