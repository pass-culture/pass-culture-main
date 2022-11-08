import React, { useCallback } from 'react'
import { useLocation } from 'react-router-dom'

import RouteLeavingGuard, {
  IShouldBlockNavigationReturnValue,
} from 'components/RouteLeavingGuard'
import useActiveFeature from 'hooks/useActiveFeature'

const STEP_OFFER = 'offer'
const STEP_OFFER_EDITION = 'offer_edition'
const STEP_STOCKS = 'stocks'
const STEP_VISIBILITY = 'visibility'
const STEP_CONFIRMATION = 'confirmation'
const STEP_RECAP = 'summary'

const collectiveUrlPatterns: { [key: string]: RegExp } = {
  [STEP_OFFER]: /\/offre\/creation\/collectif/g,
  [STEP_OFFER_EDITION]: /\/offre\/collectif\/[A-Z,0-9]+\/creation/g,
  [STEP_STOCKS]:
    /\/offre(\/(((T-){0,1}[A-Z0-9]+)|duplication))\/collectif(\/[A-Z,0-9]+)?\/stocks/g,
  [STEP_VISIBILITY]:
    /\/offre(\/([A-Z0-9]+|duplication))\/collectif(\/[A-Z,0-9]+)?\/visibilite/g,
  [STEP_RECAP]:
    /\/offre(\/(((T-){0,1}[A-Z0-9]+)|duplication))\/collectif(\/vitrine)?(\/[A-Z,0-9]+)?(\/creation)?\/recapitulatif/g,
  [STEP_CONFIRMATION]:
    /\/offre\/(((T-){0,1}[A-Z0-9]+)|duplication)\/collectif(\/vitrine)?(\/[A-Z,0-9]+)?\/confirmation/g,
}

export interface RouteLeavingGuardOfferCreationProps {
  when?: boolean
}

const RouteLeavingGuardOfferCreation = ({
  when = true,
}: RouteLeavingGuardOfferCreationProps): JSX.Element => {
  const location = useLocation()
  const isSubtypeChosenAtCreation = useActiveFeature(
    'WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION'
  )

  const shouldBlockNavigation = useCallback(
    (nextLocation: Location): IShouldBlockNavigationReturnValue => {
      let redirectPath = null
      // when multiples url match (example: offer and stocks),
      // we're keeping the last one (example: stocks)
      let from
      const fromMatchs = Object.keys(collectiveUrlPatterns).filter(
        (stepName): boolean =>
          collectiveUrlPatterns[stepName].test(location.pathname)
      )
      if (fromMatchs.length) {
        from = fromMatchs.reverse()[0]
      }

      let to
      const toMatchs = Object.keys(collectiveUrlPatterns).filter(
        (stepName): boolean =>
          nextLocation.pathname.match(collectiveUrlPatterns[stepName]) !== null
      )
      if (toMatchs.length) {
        to = toMatchs.reverse()[0]
      }

      // going back
      if (
        (from === STEP_STOCKS && to === STEP_OFFER) ||
        (from === STEP_STOCKS && to === STEP_OFFER_EDITION) ||
        (from === STEP_VISIBILITY && to === STEP_STOCKS) ||
        (from === STEP_RECAP && to === STEP_VISIBILITY) ||
        (from === STEP_RECAP && to === STEP_STOCKS)
      ) {
        if (isSubtypeChosenAtCreation) {
          return { shouldBlock: false }
        }

        redirectPath = '/offres'
        return { redirectPath, shouldBlock: true }
      }
      // going from confirmation to stock
      if (from === STEP_CONFIRMATION) {
        if (to === STEP_RECAP) {
          redirectPath = '/offres/collectives'
        }
        return { redirectPath, shouldBlock: false }
      }

      if (
        // going to stocks
        to === STEP_STOCKS ||
        // or to visibility
        to === STEP_VISIBILITY ||
        // or to confirmation
        to === STEP_CONFIRMATION ||
        // or to recap
        to === STEP_RECAP ||
        // or from collective to individual or reverse
        (from === STEP_OFFER && to === STEP_OFFER)
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

export default RouteLeavingGuardOfferCreation
