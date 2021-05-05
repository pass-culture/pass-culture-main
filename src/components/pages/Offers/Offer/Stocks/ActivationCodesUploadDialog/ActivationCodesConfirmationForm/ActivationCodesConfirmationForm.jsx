import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

const ActivationCodesConfirmationForm = ({
  activationCodes,
  clearActivationCodes,
  setActivationCodesExpirationDatetime,
  submitActivationCodes,
}) => {
  return (
    <Fragment>
      <div className="activation-codes-upload-information-message">
        <p>{`Vous êtes sur le point d'ajouter ${activationCodes.length} codes d'activation.`}</p>
        <p>{'La quantité disponible pour cette offre sera mise à jour dans vos stocks'}</p>
      </div>
      <div className="activation-codes-upload-confirmation-message">
        <p>{"Souhaitez-vous valider l'opération ?"}</p>
      </div>
      <span className="activation-codes-upload-confirmation-buttons">
        <button
          className="secondary-button activation-codes-upload-confirmation-button"
          onClick={clearActivationCodes}
          type="button"
        >
          {'Retour'}
        </button>
        <button
          className="primary-button activation-codes-upload-confirmation-button"
          onClick={submitActivationCodes}
          type="button"
        >
          {'Valider'}
        </button>
      </span>
    </Fragment>
  )
}

ActivationCodesConfirmationForm.propTypes = {
  activationCodes: PropTypes.arrayOf(PropTypes.string).isRequired,
  clearActivationCodes: PropTypes.func.isRequired,
  setActivationCodesExpirationDatetime: PropTypes.func.isRequired,
  submitActivationCodes: PropTypes.func.isRequired,
}

export default ActivationCodesConfirmationForm
