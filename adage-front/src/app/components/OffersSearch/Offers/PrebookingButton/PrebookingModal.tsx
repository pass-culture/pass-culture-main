import React from 'react'
import Modal from 'react-modal'

interface IPrebookingModal {
  closeModal: () => void
  isOpen: boolean
}
const PrebookingModal = ({
  closeModal,
  isOpen,
}: IPrebookingModal): JSX.Element => (
  <Modal
    isOpen={isOpen}
    style={{
      content: {
        width: '50%',
        height: 'fit-content',
        margin: 'auto',
      },
      overlay: {
        backgroundColor: 'rgba(0, 0, 0, 0.4)',
      },
    }}
  >
    <h3>Information</h3>
    <p>
      Votre préréservation a été effectuée avec succès !<br />
      <br /> Pour que votre chef d’établissement puisse la valider, rendez-vous
      dans la rubrique <b>Recensement</b>, puis cliquez sur <b>Recenser</b> pour
      créer ou rattacher votre offre à un projet.
    </p>
    <button
      className="prebooking-modal-button"
      onClick={closeModal}
      type="button"
    >
      J’ai compris
    </button>
  </Modal>
)

export default PrebookingModal
