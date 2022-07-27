import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import Icon from 'components/layout/Icon'
import Spinner from 'components/layout/Spinner'
import ConfirmDialog from 'new_components/ConfirmDialog'

const StocksProviderForm = ({
  saveVenueProvider,
  providerId,
  siret,
  venueId,
}) => {
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

    saveVenueProvider(payload)
    setIsConfirmDialogOpened(false)
  }, [saveVenueProvider, providerId, siret, venueId])

  if (isCheckingApi) {
    return <Spinner message="Vérification de votre rattachement" />
  }

  return (
    <>
      <form className="stocks-provider-form" onSubmit={handleOpenConfirmDialog}>
        <div className="account-section">
          <div className="account-label">Compte</div>
          <div className="account-value">{siret}</div>
        </div>
        <div className="provider-import-button-container">
          <button className="secondary-button" type="submit">
            Importer
          </button>
        </div>
      </form>
      {isConfirmDialogOpened && (
        <ConfirmDialog
          cancelText="Annuler"
          confirmText="Continuer"
          onCancel={handleCloseConfirmDialog}
          onConfirm={handleFormSubmit}
          title="Certains ouvrages seront exclus de la synchronisation automatique."
        >
          <p>
            Vous pouvez retrouver la liste des catégories de livres qui sont
            exclus de la synchronisation automatique en suivant le lien
            <a
              className="tertiary-link"
              href="https://aide.passculture.app/hc/fr/articles/4412007214225"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon
                alt="lien externe, nouvel onglet"
                svg="ico-external-site-red"
              />
              FAQ
            </a>
          </p>
        </ConfirmDialog>
      )}
    </>
  )
}

StocksProviderForm.propTypes = {
  providerId: PropTypes.string.isRequired,
  saveVenueProvider: PropTypes.func.isRequired,
  siret: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
}

export default StocksProviderForm
