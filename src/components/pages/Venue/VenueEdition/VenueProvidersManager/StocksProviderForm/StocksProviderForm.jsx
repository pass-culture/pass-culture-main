import PropTypes from 'prop-types'
import React, { useState, useCallback } from 'react'

import Spinner from 'components/layout/Spinner'

const StocksProviderForm = ({
  cancelProviderSelection,
  createVenueProvider,
  historyPush,
  notify,
  offererId,
  providerId,
  siret,
  venueId,
}) => {
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
        .then(() => {
          historyPush(`/structures/${offererId}/lieux/${venueId}`)
        })
        .catch(error => {
          notify(error.errors)
          cancelProviderSelection()
        })
    },
    [
      cancelProviderSelection,
      createVenueProvider,
      historyPush,
      notify,
      offererId,
      providerId,
      siret,
      venueId,
    ]
  )

  if (isCheckingApi) {
    return <Spinner message="Vérification de votre rattachement" />
  }

  return (
    <form
      className="provider-form"
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
  cancelProviderSelection: PropTypes.func.isRequired,
  createVenueProvider: PropTypes.func.isRequired,
  historyPush: PropTypes.func.isRequired,
  notify: PropTypes.func.isRequired,
  offererId: PropTypes.string.isRequired,
  providerId: PropTypes.string.isRequired,
  siret: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
}

export default StocksProviderForm
