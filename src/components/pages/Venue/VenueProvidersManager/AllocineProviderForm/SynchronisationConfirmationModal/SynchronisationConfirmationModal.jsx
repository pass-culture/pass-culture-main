import React from 'react'
import PropTypes from 'prop-types'

const SynchronisationConfirmationModal = ({ handleClose, handleConfirm }) => {
  return (
    <div className="fond">
      <section className="modal-main">
        <div className="confirmation-modal-content">
          <p className="warning-text">
            {'Vous ne pourrez plus modifier le prix de vente après la synchronisation.'}
          </p>
          <div className="actions">
            <button
              className="cancel-button"
              id="cancel-button"
              onClick={handleClose}
              type="button"
            >
              {'Annuler'}
            </button>
            <button
              className="confirm-button"
              id="confirm-button"
              onClick={handleConfirm}
            >
              {'Synchroniser'}
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}

SynchronisationConfirmationModal.propTypes = {
  handleClose: PropTypes.func.isRequired,
}

export default SynchronisationConfirmationModal
