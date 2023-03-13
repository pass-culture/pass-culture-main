import React, { useCallback } from 'react'
import { useLocation } from 'react-router-dom-v5-compat'

import RouteLeavingGuard, {
  IShouldBlockNavigationReturnValue,
} from 'components/RouteLeavingGuard/RouteLeavingGuard'

import { shouldBlockNavigation } from './utils'
export interface RouteLeavingGuardCollectiveOfferCreationProps {
  when?: boolean
}

const RouteLeavingGuardCollectiveOfferCreation = ({
  when = true,
}: RouteLeavingGuardCollectiveOfferCreationProps): JSX.Element => {
  const location = useLocation()

  const shouldBlock = useCallback(
    (nextLocation: Location): IShouldBlockNavigationReturnValue => {
      return shouldBlockNavigation({ currentLocation: location, nextLocation })
    },
    [location]
  )

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlock}
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

export default RouteLeavingGuardCollectiveOfferCreation
