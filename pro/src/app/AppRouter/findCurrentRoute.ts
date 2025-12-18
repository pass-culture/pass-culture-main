import { type Location, matchPath } from 'react-router'

import { routes } from '@/app/AppRouter/routesMap'
import {
  routesIndividualOfferWizard,
  routesOnboardingIndividualOfferWizard,
} from '@/app/AppRouter/subroutesIndividualOfferWizardMap'
import { routesSignupJourney } from '@/app/AppRouter/subroutesSignupJourneyMap'
import { routesSignup } from '@/app/AppRouter/subroutesSignupMap'

import { routesReimbursements } from './subroutesReimbursements'
import type { CustomRouteObject } from './types'

// TODO (igabriele, 2025-12-17): Replace this very custom implementation with react-router official `matchRoutes`.
export const findCurrentRoute = (
  location: Location
): CustomRouteObject | undefined =>
  [
    ...routes,
    ...routesIndividualOfferWizard,
    ...routesOnboardingIndividualOfferWizard,
    ...routesSignup,
    ...routesSignupJourney,
    ...routesReimbursements,
  ]
    // This reverse is here so that subroutes (e.g. /inscription/compte/confirmation)
    // are matched before their parents (e.g. /inscription/*)
    .reverse()
    .find(
      ({ path }: CustomRouteObject) =>
        matchPath(path, location.pathname) !== null
    )
