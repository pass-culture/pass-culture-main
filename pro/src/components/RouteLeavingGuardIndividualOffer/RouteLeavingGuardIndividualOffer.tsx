import React from 'react'

import RouteLeavingGuard, {
  BlockerFunction,
} from 'components/RouteLeavingGuard'

interface RouteLeavingGuardIndividualOffer {
  when: boolean
}

export const RouteLeavingGuardIndividualOffer = ({
  when,
}: RouteLeavingGuardIndividualOffer): JSX.Element => {
  const shouldBlockNavigation: BlockerFunction = () => when

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
      dialogTitle="Les informations non enregistrées seront perdues"
      leftButton="Quitter la page"
      rightButton="Rester sur la page"
      closeModalOnRightButton
    />
  )
}
