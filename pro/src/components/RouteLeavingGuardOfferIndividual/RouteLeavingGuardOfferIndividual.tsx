import React from 'react'

import RouteLeavingGuard from 'components/RouteLeavingGuard'

export interface IRouteLeavingGuardOfferIndividual {
  tracking?: (p: string) => void
  when: boolean
}

const RouteLeavingGuardOfferIndividual = ({
  tracking,
  when,
}: IRouteLeavingGuardOfferIndividual): JSX.Element => {
  const shouldBlockNavigation = (chosenLocation: Location) => ({
    shouldBlock: true,
    redirectPath: chosenLocation.pathname,
  })

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
      when={when}
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
