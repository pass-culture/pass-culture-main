import React from 'react'

import RouteLeavingGuard, {
  BlockerFunction,
} from 'components/RouteLeavingGuard'

export interface RouteLeavingGuardCollectiveOfferCreationProps {
  isFormDirty: boolean
}

const RouteLeavingGuardVenueCollectiveDataEdition = ({
  isFormDirty,
}: RouteLeavingGuardCollectiveOfferCreationProps): JSX.Element => {
  const shouldBlockNavigation: BlockerFunction = () => isFormDirty

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
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
