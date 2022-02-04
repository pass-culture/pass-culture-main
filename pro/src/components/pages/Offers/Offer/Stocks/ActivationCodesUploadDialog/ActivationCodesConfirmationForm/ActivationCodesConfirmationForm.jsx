import PropTypes from 'prop-types'
import React from 'react'

import DateInput from 'components/layout/inputs/DateInput/DateInput'

const ActivationCodesConfirmationForm = ({
  activationCodes,
  activationCodesExpirationDatetime,
  bookingLimitDatetime,
  changeActivationCodesExpirationDatetime,
  clearActivationCodes,
  submitActivationCodes,
  today,
}) => {
  const getMinimumExpirationDatetime = () => {
    const result = new Date(bookingLimitDatetime)
    result.setDate(result.getDate() + 7)
    return result
  }

  return (
    <div className="activation-codes-upload-confirmation-form">
      <div className="activation-codes-upload-information-message">
        <p>
          Vous êtes sur le point d’ajouter {activationCodes.length} codes
          d’activation.
        </p>
        <p>
          La quantité disponible pour cette offre sera mise à jour dans vos
          stocks.
        </p>
        <p className="expiration-date-information-message">
          Veuillez ajouter une date de fin de validité. Cette date ne doit pas
          être antérieure à la date limite de réservation.
        </p>
      </div>
      <div className="resized-input expiration-datetime-input-container">
        <label className="expiration-datetime-label">
          <div className="labels">
            Date limite de validité{' '}
            <span className="it-sub-label">optionnel</span>
          </div>
        </label>
        <DateInput
          ariaLabel="Date limite de validité"
          dateTime={activationCodesExpirationDatetime}
          minDateTime={
            bookingLimitDatetime ? getMinimumExpirationDatetime() : null
          }
          onChange={changeActivationCodesExpirationDatetime}
          openingDateTime={today}
        />
      </div>
      <div className="activation-codes-upload-confirmation-message">
        <p>
          Vous ne pourrez modifier ni la quantité ni la date de validité après
          import.
        </p>
        <p>Souhaitez-vous valider l’opération ?</p>
      </div>
      <span className="activation-codes-upload-confirmation-buttons">
        <button
          className="secondary-button activation-codes-upload-confirmation-button"
          onClick={clearActivationCodes}
          type="button"
        >
          Retour
        </button>
        <button
          className="primary-button activation-codes-upload-confirmation-button"
          onClick={submitActivationCodes}
          type="button"
        >
          Valider
        </button>
      </span>
    </div>
  )
}

ActivationCodesConfirmationForm.defaultProps = {
  activationCodesExpirationDatetime: null,
  bookingLimitDatetime: null,
}

ActivationCodesConfirmationForm.propTypes = {
  activationCodes: PropTypes.arrayOf(PropTypes.string).isRequired,
  activationCodesExpirationDatetime: PropTypes.instanceOf(Date),
  bookingLimitDatetime: PropTypes.instanceOf(Date),
  changeActivationCodesExpirationDatetime: PropTypes.func.isRequired,
  clearActivationCodes: PropTypes.func.isRequired,
  submitActivationCodes: PropTypes.func.isRequired,
  today: PropTypes.instanceOf(Date).isRequired,
}

export default ActivationCodesConfirmationForm
