import React from 'react'

import RouteLeavingGuard from 'components/RouteLeavingGuard/RouteLeavingGuard'

import { shouldBlockNavigation } from './utils'

export const RouteLeavingGuardCollectiveOfferCreation = (): JSX.Element => {
  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
      dialogTitle="Voulez-vous quitter la création d’offre ?"
    >
      <p>
        Votre offre ne sera pas sauvegardée et toutes les informations seront
        perdues.
      </p>
    </RouteLeavingGuard>
  )
}
