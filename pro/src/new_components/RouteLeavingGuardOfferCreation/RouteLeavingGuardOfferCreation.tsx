import React, { useCallback } from 'react'
import { useLocation } from 'react-router-dom'

import RouteLeavingGuard, {
  IShouldBlockNavigationReturnValue,
} from 'new_components/RouteLeavingGuard'

const STEP_OFFER = 'offer'
const STEP_STOCKS = 'stocks'
const STEP_VISIBILITY = 'visibility'
const STEP_CONFIRMATION = 'confirmation'

const individualUrlPatterns: { [key: string]: RegExp } = {
  [STEP_OFFER]: /\/offre\/([A-Z0-9]+\/)?individuel\/creation/g,
  [STEP_STOCKS]: /\/offre\/([A-Z0-9]+)\/individuel\/creation\/stocks/g,
  [STEP_CONFIRMATION]:
    /\/offre\/([A-Z0-9]+)\/individuel\/creation\/confirmation/g,
}
const collectiveUrlPatterns: { [key: string]: RegExp } = {
  [STEP_OFFER]: /\/offre\/creation\/collectif/g,
  [STEP_STOCKS]: /\/offre\/((T-){0,1}[A-Z0-9]+)\/collectif\/stocks/g,
  [STEP_VISIBILITY]:
    /\/offre(\/([A-Z0-9]+|duplication))\/collectif(\/[A-Z,0-9]+)?\/visibilite/g,
  [STEP_CONFIRMATION]:
    /\/offre\/(((T-){0,1}[A-Z0-9]+)|duplication)\/collectif(\/[A-Z,0-9]+)?\/confirmation/g,
}

export interface RouteLeavingGuardOfferCreationProps {
  when?: boolean
  isCollectiveFlow?: boolean
}

const RouteLeavingGuardOfferCreation = ({
  when = true,
  isCollectiveFlow = false,
}: RouteLeavingGuardOfferCreationProps): JSX.Element => {
  const location = useLocation()

  const shouldBlockNavigation = useCallback(
    (nextLocation: Location): IShouldBlockNavigationReturnValue => {
      let redirectPath = null
      const urlPatterns = isCollectiveFlow
        ? collectiveUrlPatterns
        : individualUrlPatterns

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

      // going from stock to offer
      if (from === STEP_STOCKS && to === STEP_OFFER) {
        redirectPath = '/offres'
        return { redirectPath, shouldBlock: true }
      }

      // going from confirmation to stock
      if (from === STEP_CONFIRMATION) {
        if (
          to === STEP_STOCKS ||
          (isCollectiveFlow && to === STEP_VISIBILITY)
        ) {
          redirectPath = '/offres'
        }
        return { redirectPath, shouldBlock: false }
      }
      if (
        // going to stocks
        to === STEP_STOCKS ||
        // or to visibility
        (isCollectiveFlow && to === STEP_VISIBILITY) ||
        // or to confirmation
        to === STEP_CONFIRMATION ||
        // or from collective to individual or reverse
        (from === STEP_OFFER && to === STEP_OFFER)
      ) {
        return { shouldBlock: false }
      }
      return { shouldBlock: true }
    },
    [location, isCollectiveFlow]
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

export default RouteLeavingGuardOfferCreation
