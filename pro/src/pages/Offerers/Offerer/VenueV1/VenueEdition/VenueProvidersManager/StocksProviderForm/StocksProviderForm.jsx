import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Icon from 'ui-kit/Icon/Icon'
import Spinner from 'ui-kit/Spinner/Spinner'

import styles from './StocksProviderForm.module.scss'

const StocksProviderForm = ({
  saveVenueProvider,
  providerId,
  siret,
  venueId,
  hasOffererProvider,
}) => {
  const [isCheckingApi, setIsCheckingApi] = useState(false)
  const [isConfirmDialogOpened, setIsConfirmDialogOpened] = useState(false)

  const handleOpenConfirmDialog = useCallback(event => {
    event.preventDefault()
    event.stopPropagation()
    setIsConfirmDialogOpened(true)
  }, [])

  const handleCloseConfirmDialog = useCallback(() => {
    /* istanbul ignore next: DEBT, TO FIX */
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
      <div className={styles['stocks-provider-form']}>
        {!hasOffererProvider && (
          <div className="account-section">
            <div className="account-label">Compte</div>
            <div className="account-value">{siret}</div>
          </div>
        )}
        <div className="provider-import-button-container">
          <Button
            variant={ButtonVariant.SECONDARY}
            onClick={handleOpenConfirmDialog}
          >
            Importer
          </Button>
        </div>
      </div>
      {isConfirmDialogOpened && (
        <ConfirmDialog
          cancelText="Annuler"
          confirmText="Continuer"
          onCancel={handleCloseConfirmDialog}
          onConfirm={handleFormSubmit}
          title="Certaines offres ne seront pas synchronisées"
        >
          <p>
            Le pass Culture ne permet l’import automatique que des offres dans
            les catégories support audio et livres à l’heure actuelle. Certains
            rayons ne seront en outre pas synchronisés. Notre FAQ vous décriera
            les règles précisément.
            <a
              className="tertiary-link"
              href="https://aide.passculture.app/hc/fr/articles/4411999024401--Acteurs-Culturels-Quels-sont-les-livres-%C3%A9ligibles-au-pass-Culture-"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon
                alt="lien externe, nouvel onglet"
                svg="ico-external-site-red"
              />
            </a>
          </p>
        </ConfirmDialog>
      )}
    </>
  )
}

StocksProviderForm.propTypes = {
  providerId: PropTypes.number.isRequired,
  saveVenueProvider: PropTypes.func.isRequired,
  siret: PropTypes.string.isRequired,
  venueId: PropTypes.number.isRequired,
  hasOffererProvider: PropTypes.bool.isRequired,
}

export default StocksProviderForm
