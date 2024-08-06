import React from 'react'

import { RouteLeavingGuard } from 'components/RouteLeavingGuard/RouteLeavingGuard'

import { shouldBlockNavigation } from './utils'

export const RouteLeavingGuardCollectiveOfferCreation = (): JSX.Element => {
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
