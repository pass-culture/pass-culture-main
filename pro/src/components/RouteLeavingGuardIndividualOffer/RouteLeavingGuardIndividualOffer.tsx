import React from 'react'

import {
  RouteLeavingGuard,
  BlockerFunction,
} from 'components/RouteLeavingGuard/RouteLeavingGuard'

interface RouteLeavingGuardIndividualOffer {
  when: boolean
}

export const RouteLeavingGuardIndividualOffer = ({
  when,
}: RouteLeavingGuardIndividualOffer): JSX.Element => {
  const shouldBlockNavigation: BlockerFunction = ({
    currentLocation,
    nextLocation,
  }) => when && currentLocation.pathname !== nextLocation.pathname

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
