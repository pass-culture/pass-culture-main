import React from 'react'
import PropTypes from 'prop-types'
import {ROOT_PATH} from '../../../../../../utils/config'

const SynchronisationConfirmationModal = ({ handleClose, handleConfirm }) => {
  return (
    <div className="background">
      <section className="modal-main">
        <div className="confirmation-modal-content">
          <div className="warning-text">
            <img
              alt="Attention"
              src={`${ROOT_PATH}/icons/picto-warning-orange.png`}
              title="Attention"
            />
            <p>
              {'Vous ne pourrez plus modifier le prix de vente après la synchronisation.'}
            </p>
          </div>
          <div className="actions">
            <button
              className="cancel-button"
              id="cancel-button"
              onClick={handleClose}
              type="button"
            >
              <p>
                {' Annuler '}
              </p>
            </button>
            <button
              className="confirm-button"
              id="confirm-button"
              onClick={handleConfirm}
              type="button"
            >
              <b>
                {' Synchroniser '}
              </b>
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
