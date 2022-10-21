import React, { useCallback } from 'react'
import { useLocation } from 'react-router-dom'

import RouteLeavingGuard, {
  IShouldBlockNavigationReturnValue,
} from 'new_components/RouteLeavingGuard'

const STEP_OFFER = 'offer'
const STEP_STOCKS = 'stocks'
const STEP_SUMMARY = 'recapitulatif'
const STEP_CONFIRMATION = 'confirmation'

const DRAFT_STATE = 'brouillon'

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

      const urlMatch = nextLocation.pathname.match(/[a-z]+$/)
      const stateName = urlMatch && urlMatch[0]
      if (stateName === DRAFT_STATE) {
        return { shouldBlock: false }
      }

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
      shouldBlockNavigation={shouldBlockNavigation}
      when={when}
      dialogTitle="Voulez-vous quitter la création d’offre ?"
    >
      <p>
        Votre offre ne sera pas sauvegardée et toutes les informations seront
        perdues.
      </p>
    </RouteLeavingGuard>
  )
}

export default RouteLeavingGuardOfferIndividual
