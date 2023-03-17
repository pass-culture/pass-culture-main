import React from 'react'

import RouteLeavingGuard, {
  BlockerFunction,
} from 'components/RouteLeavingGuard'

export interface IRouteLeavingGuardOfferIndividual {
  tracking?: (p: string) => void
  when: boolean
}

const RouteLeavingGuardOfferIndividual = ({
  tracking,
  when,
}: IRouteLeavingGuardOfferIndividual): JSX.Element => {
  const shouldBlockNavigation: BlockerFunction = () => when

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
      dialogTitle="Les informations non sauvegardées seront perdues"
      leftButton="Quitter la page"
      rightButton="Rester sur la page"
      tracking={tracking}
      closeModalOnRightButton
    >
      <p>
        Restez sur la page et cliquez sur "Sauvegarder le brouillon" pour ne
        rien perdre de vos modifications.
      </p>
    </RouteLeavingGuard>
  )
}

export default RouteLeavingGuardOfferIndividual
