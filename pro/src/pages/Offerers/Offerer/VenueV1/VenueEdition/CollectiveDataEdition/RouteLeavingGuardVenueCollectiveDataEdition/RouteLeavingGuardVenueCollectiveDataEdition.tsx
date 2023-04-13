import React from 'react'

import RouteLeavingGuard, {
  BlockerFunction,
} from 'components/RouteLeavingGuard'

export interface RouteLeavingGuardCollectiveOfferCreationProps {
  shouldBlock: boolean
}

const RouteLeavingGuardVenueCollectiveDataEdition = ({
  shouldBlock,
}: RouteLeavingGuardCollectiveOfferCreationProps): JSX.Element => {
  const shouldBlockNavigation: BlockerFunction = () => shouldBlock

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
