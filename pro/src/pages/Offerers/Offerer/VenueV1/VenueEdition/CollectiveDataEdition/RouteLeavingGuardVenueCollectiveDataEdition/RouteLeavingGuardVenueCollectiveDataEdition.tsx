import React from 'react'

import RouteLeavingGuard, {
  IShouldBlockNavigationReturnValue,
} from 'components/RouteLeavingGuard'

export interface RouteLeavingGuardCollectiveOfferCreationProps {
  isFormDirty: boolean
}

const RouteLeavingGuardVenueCollectiveDataEdition = ({
  isFormDirty,
}: RouteLeavingGuardCollectiveOfferCreationProps): JSX.Element => {
  const shouldBlockNavigation = (): IShouldBlockNavigationReturnValue => ({
    shouldBlock: isFormDirty,
  })

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
      when
      dialogTitle="Voulez vous quitter la page d’informations pour les enseignants ?"
    >
      <p>
        Vos informations ne seront pas sauvegardées et toutes les informations
        seront perdues.
      </p>
    </RouteLeavingGuard>
  )
}

export default RouteLeavingGuardVenueCollectiveDataEdition
