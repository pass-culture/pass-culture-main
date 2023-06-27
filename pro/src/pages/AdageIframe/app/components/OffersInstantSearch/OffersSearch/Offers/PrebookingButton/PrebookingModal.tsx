import React from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import PasscultureIcon from 'icons/ico-passculture.svg'

interface IPrebookingModal {
  closeModal: () => void
  preBookCurrentStock: () => Promise<void>
}
const PrebookingModal = ({
  closeModal,
  preBookCurrentStock,
}: IPrebookingModal): JSX.Element => {
  return (
    <ConfirmDialog
      icon={PasscultureIcon}
      onConfirm={preBookCurrentStock}
      onCancel={closeModal}
      title="Êtes-vous sûr de vouloir préréserver ?"
      confirmText="Préréserver"
      cancelText="Fermer"
      extraClassNames="prebooking-modal"
    >
      <p className="prebooking-modal-text">
        Si oui, une fois votre préréservation confirmée :
        <br />
        <br />
        <strong>1) Rattachez votre préréservation à un projet </strong>: pour
        cela rendez-vous sous la rubrique <strong>Projets EAC</strong>, puis
        cliquez sur <strong>Les Projets </strong>
        pour créer un projet et rattacher votre préréservation à votre nouveau
        projet ou à un projet existant
        <br />
        <br />
        <strong>2)</strong> Votre chef d’établissement pourra alors{' '}
        <strong>confirmer la préréservation</strong>
      </p>
    </ConfirmDialog>
  )
}

export default PrebookingModal
