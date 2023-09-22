import React from 'react'

import RouteLeavingGuard, {
  BlockerFunction,
} from 'components/RouteLeavingGuard'

interface RouteLeavingGuardIndividualOffer {
  when: boolean
  isEdition: boolean
}

const RouteLeavingGuardIndividualOffer = ({
  when,
  isEdition,
}: RouteLeavingGuardIndividualOffer): JSX.Element => {
  const shouldBlockNavigation: BlockerFunction = () => when

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
      dialogTitle="Les informations non sauvegardées seront perdues"
      leftButton="Quitter la page"
      rightButton="Rester sur la page"
      closeModalOnRightButton
    >
      <p>
        {isEdition
          ? 'Restez sur la page et cliquez sur “Enregistrer les modifications” pour ne rien perdre de vos modifications.'
          : 'Restez sur la page et cliquez sur “Sauvegarder le brouillon” pour ne rien perdre de vos modifications.'}
      </p>
    </RouteLeavingGuard>
  )
}

export default RouteLeavingGuardIndividualOffer
