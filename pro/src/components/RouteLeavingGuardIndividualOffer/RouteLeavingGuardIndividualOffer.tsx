import React from 'react'

import RouteLeavingGuard, {
  BlockerFunction,
} from 'components/RouteLeavingGuard'

interface RouteLeavingGuardIndividualOffer {
  when: boolean
}

const RouteLeavingGuardIndividualOffer = ({
  when,
}: RouteLeavingGuardIndividualOffer): JSX.Element => {
  const shouldBlockNavigation: BlockerFunction = () => when

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
      dialogTitle="Les informations non sauvegardées seront perdues"
      leftButton="Quitter la page"
      rightButton="Rester sur la page"
      closeModalOnRightButton
    />
  )
}

export default RouteLeavingGuardIndividualOffer
