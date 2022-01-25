import React, { useState } from 'react'
import Modal from 'react-modal'

import Button from 'app/ui-kit/Button'
import { ReactComponent as Logo } from 'assets/logo-without-text.svg'

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
  const [isLoading, setIsLoading] = useState(false)

  const handlePrebookCurrentStock = async () => {
    setIsLoading(true)
    await preBookCurrentStock()
    setIsLoading(false)
  }

  return (
    <Modal
      isOpen={isOpen}
      style={{
        content: {
          width: '452px',
          height: 'fit-content',
          margin: 'auto',
          padding: '48px 48px 24px',
          boxSizing: 'border-box',
          fontSize: '15px',
          borderRadius: '10px',
        },
        overlay: {
          backgroundColor: 'rgba(0, 0, 0, 0.4)',
        },
      }}
    >
      <Logo className="prebooking-modal-logo" />
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
        <b>approuver la préréservation</b>.
      </p>
      <div className="prebooking-modal-buttons">
        <Button
          className="prebooking-modal-button"
          label="Fermer"
          onClick={closeModal}
          variant="primary"
        />
        <Button
          className="prebooking-modal-button"
          isLoading={isLoading}
          label="Préréserver"
          onClick={handlePrebookCurrentStock}
        />
      </div>
    </Modal>
  )
}

export default PrebookingModal
