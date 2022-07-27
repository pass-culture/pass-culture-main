import React, { useCallback } from 'react'
import { useLocation } from 'react-router-dom'

import { LeavingOfferCreationDialog } from 'new_components/LeavingOfferCreationDialog'
import RouteLeavingGuard, {
  IShouldBlockNavigationReturnValue,
} from 'new_components/RouteLeavingGuard'

const STEP_OFFER = 'offer'
const STEP_STOCKS = 'stocks'
const STEP_SUMMARY = 'recapitulatif'
const STEP_CONFIRMATION = 'confirmation'

const urlPatterns: { [key: string]: RegExp } = {
  [STEP_OFFER]: /\/offre\/([A-Z0-9]+\/)?individuel\/creation/g,
  [STEP_STOCKS]: /\/offre\/([A-Z0-9]+)\/individuel\/creation\/stocks/g,
  [STEP_SUMMARY]: /\/offre\/([A-Z0-9]+)\/individuel\/creation\/recapitulatif/g,
  [STEP_CONFIRMATION]:
    /\/offre\/([A-Z0-9]+)\/individuel\/creation\/confirmation/g,
}

export interface RouteLeavingGuardOfferIndividualProps {
  when?: boolean
}

const RouteLeavingGuardOfferIndividual = ({
  when = true,
}: RouteLeavingGuardOfferIndividualProps): JSX.Element => {
  const location = useLocation()
  const shouldBlockNavigation = useCallback(
    (nextLocation: Location): IShouldBlockNavigationReturnValue => {
      let redirectPath = null

      // when multiples url match (example: offer and stocks),
      // we're keeping the last one (example: stocks)
      let from
      const fromMatchs = Object.keys(urlPatterns).filter((stepName): boolean =>
        urlPatterns[stepName].test(location.pathname)
      )
      if (fromMatchs.length) {
        from = fromMatchs.reverse()[0]
      }

      let to
      const toMatchs = Object.keys(urlPatterns).filter(
        (stepName): boolean =>
          nextLocation.pathname.match(urlPatterns[stepName]) !== null
      )
      if (toMatchs.length) {
        to = toMatchs.reverse()[0]
      }

      if (from == STEP_OFFER) {
        if (to === undefined) {
          return {
            redirectPath: '/offres',
            shouldBlock: true,
          }
        }
      }

      // going from confirmation to summary
      if (from === STEP_CONFIRMATION) {
        if (to === STEP_SUMMARY) {
          redirectPath = '/offres' // TODO go to edition recapitulatif
        }
        return { redirectPath, shouldBlock: false }
      }

      // going to stocks
      // or to visibility
      // or to confirmation
      if (
        to === STEP_OFFER ||
        to === STEP_STOCKS ||
        to === STEP_SUMMARY ||
        to === STEP_CONFIRMATION
      ) {
        return { shouldBlock: false }
      }
      return { shouldBlock: true }
    },
    [location]
  )
  return (
    <RouteLeavingGuard
      labelledBy="LEAVING_OFFER_CREATION_LABEL_ID"
      shouldBlockNavigation={shouldBlockNavigation}
      when={when}
    >
      <LeavingOfferCreationDialog />
    </RouteLeavingGuard>
  )
}

export default RouteLeavingGuardOfferIndividual
