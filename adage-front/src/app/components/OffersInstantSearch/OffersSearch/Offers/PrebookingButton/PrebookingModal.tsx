import React from 'react'

import { ModalLayout } from 'app/ui-kit'

interface IPrebookingModal {
  closeModal: () => void
  isOpen: boolean
  preBookCurrentStock: () => Promise<void>
}
const PrebookingModal = ({
  closeModal,
  isOpen,
  preBookCurrentStock,
}: IPrebookingModal): JSX.Element => {
  return (
    <ModalLayout
      action={preBookCurrentStock}
      actionLabel="Préréserver"
      closeModal={closeModal}
      isOpen={isOpen}
    >
      <h3 className="prebooking-modal-title">
        Êtes-vous sûr de vouloir préréserver ?
      </h3>
      <p className="prebooking-modal-text">
        Si oui, une fois votre préréservation confirmée :
        <br />
        <br />
        <b>1) Rattachez votre préréservation à un projet </b>: pour cela
        rendez-vous sous la rubrique <b>Recensement</b>, puis cliquez sur{' '}
        <b>Recenser </b>
        pour créer un projet et rattacher votre préréservation à votre nouveau
        projet ou à un projet existant.
        <br />
        <br />
        <b>2)</b> Votre chef d’établissement pourra alors{' '}
        <b>confirmer la préréservation</b>.
      </p>
    </ModalLayout>
  )
}

export default PrebookingModal
