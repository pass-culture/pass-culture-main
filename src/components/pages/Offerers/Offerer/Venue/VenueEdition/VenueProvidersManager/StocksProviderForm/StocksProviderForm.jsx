import PropTypes from 'prop-types'
import React, { useState, useCallback } from 'react'

import Spinner from 'components/layout/Spinner'

const StocksProviderForm = ({ createVenueProvider, providerId, siret, venueId }) => {
  const [isCheckingApi, setIsCheckingApi] = useState(false)

  const handleFormSubmit = useCallback(
    event => {
      event.preventDefault()

      setIsCheckingApi(true)

      const payload = {
        providerId,
        venueIdAtOfferProvider: siret,
        venueId,
      }

      createVenueProvider(payload)
    },
    [createVenueProvider, providerId, siret, venueId]
  )

  if (isCheckingApi) {
    return <Spinner message="Vérification de votre rattachement" />
  }

  return (
    <form
      className="stocks-provider-form"
      onSubmit={handleFormSubmit}
    >
      <div className="account-section">
        <div className="account-label">
          {'Compte'}
        </div>
        <div className="account-value">
          {siret}
        </div>
      </div>
      <div className="provider-import-button-container">
        <button
          className="secondary-button"
          type="submit"
        >
          {'Importer'}
        </button>
      </div>
    </form>
  )
}

StocksProviderForm.propTypes = {
  createVenueProvider: PropTypes.func.isRequired,
  providerId: PropTypes.string.isRequired,
  siret: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
}

export default StocksProviderForm
