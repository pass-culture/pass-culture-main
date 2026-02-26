import { type Location, matchPath } from 'react-router'

import { routes } from '@/app/AppRouter/routesMap'
import {
  routesIndividualOfferWizard,
  routesOnboardingIndividualOfferWizard,
} from '@/app/AppRouter/subroutesIndividualOfferWizardMap'
import { routesSignupJourney } from '@/app/AppRouter/subroutesSignupJourneyMap'
import { routesSignup } from '@/app/AppRouter/subroutesSignupMap'
import { routesWelcomeCarousel } from '@/app/AppRouter/subroutesWelcomeCarousel'

import { administrationRouteGroup } from './routes/administrationRouteGroup'
import { partnerRouteGroup } from './routes/partnerRouteGroup'
import { reimbursementsRouteGroup } from './routes/reimbursementsRouteGroup'
import type { CustomRouteGroupChild, CustomRouteOrphan } from './types'

/** @deprecated Use `useCurrentRoute()`. */
export const findCurrentRoute = (location: Location) =>
  [
    ...routes,
    ...routesIndividualOfferWizard,
    ...routesOnboardingIndividualOfferWizard,
    ...routesSignup,
    ...routesSignupJourney,
    ...routesWelcomeCarousel,

    // Legacy compatibility (pre-`WIP_SWITCH_VENUE` FF)
    ...administrationRouteGroup.children.map((routeGroupChild) => ({
      ...routeGroupChild,
      path: `${administrationRouteGroup.path}/${routeGroupChild.path}`,
    })),
    ...partnerRouteGroup.children.map((routeGroupChild) => ({
      ...routeGroupChild,
      path: `${partnerRouteGroup.path}/${routeGroupChild.path}`,
    })),
    ...reimbursementsRouteGroup.children.map((routeGroupChild) => ({
      ...routeGroupChild,
      path: `${reimbursementsRouteGroup.path}/${routeGroupChild.path}`,
    })),
  ]
    // This reverse is here so that subroutes (e.g. /inscription/compte/confirmation)
    // are matched before their parents (e.g. /inscription/*)
    .reverse()
    .filter((route) => route.path !== '')
    .find(({ path }) => matchPath(path, location.pathname) !== null) as
    | CustomRouteOrphan
    | CustomRouteGroupChild
    | undefined
