/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React, { useState, useCallback } from 'react'

import Spinner from 'components/layout/Spinner'

import ConfirmDialog from '../ConfirmDialog/ConfirmDialog'

const StocksProviderForm = ({ createVenueProvider, providerId, siret, venueId }) => {
  const [isCheckingApi, setIsCheckingApi] = useState(false)
  const [isConfirmDialogOpened, setIsConfirmDialogOpened] = useState(false)

  const handleOpenConfirmDialog = useCallback(event => {
    event.preventDefault()
    setIsConfirmDialogOpened(true)
  }, [])

  const handleCloseConfirmDialog = useCallback(() => {
    setIsConfirmDialogOpened(false)
  }, [])

  const handleFormSubmit = useCallback(() => {
    setIsCheckingApi(true)

    const payload = {
      providerId,
      venueIdAtOfferProvider: siret,
      venueId,
    }

    createVenueProvider(payload)
    setIsConfirmDialogOpened(false)
  }, [createVenueProvider, providerId, siret, venueId])

  if (isCheckingApi) {
    return <Spinner message="Vérification de votre rattachement" />
  }

  return (
    <>
      <form
        className="stocks-provider-form"
        onSubmit={handleOpenConfirmDialog}
      >
        <div className="account-section">
          <div className="account-label">
            Compte
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
            Importer
          </button>
        </div>
      </form>
      {isConfirmDialogOpened && (
        <ConfirmDialog
          onCancel={handleCloseConfirmDialog}
          onConfirm={handleFormSubmit}
        />
      )}
    </>
  )
}

StocksProviderForm.propTypes = {
  createVenueProvider: PropTypes.func.isRequired,
  providerId: PropTypes.string.isRequired,
  siret: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
}

export default StocksProviderForm
