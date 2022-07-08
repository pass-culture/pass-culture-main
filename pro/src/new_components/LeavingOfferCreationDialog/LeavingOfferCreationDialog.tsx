import LeavingGuardDialog from 'new_components/LeavingGuardDialog'
import React from 'react'

const LeavingOfferCreationDialog = (): JSX.Element => {
  return (
    <LeavingGuardDialog
      title="Voulez-vous quitter la création d’offre ?"
      message="Votre offre ne sera pas sauvegardée et toutes les informations seront
        perdues."
    />
  )
}

export default LeavingOfferCreationDialog
