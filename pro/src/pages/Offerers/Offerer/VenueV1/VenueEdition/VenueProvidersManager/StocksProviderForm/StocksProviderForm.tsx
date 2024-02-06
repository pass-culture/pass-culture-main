import React, { useState } from 'react'

import { PostVenueProviderBody } from 'apiClient/v1'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullLinkIcon from 'icons/full-link.svg'
import strokeConnectIcon from 'icons/stroke-connect.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import styles from './StocksProviderForm.module.scss'

interface PayloadProps {
  providerId: number
  venueIdAtOfferProvider: string
  venueId: number
}

export interface StocksProviderFormProps {
  offererId: number
  providerId: number
  saveVenueProvider: (payload: PostVenueProviderBody) => boolean
  siret: string
  venueId: number
  hasApiKey: boolean
}

const StocksProviderForm = ({
  saveVenueProvider,
  providerId,
  siret,
  venueId,
  hasApiKey,
  offererId,
}: StocksProviderFormProps) => {
  const { logEvent } = useAnalytics()
  const [isCheckingApi, setIsCheckingApi] = useState(false)
  const [isConfirmDialogOpened, setIsConfirmDialogOpened] = useState(false)

  const handleOpenConfirmDialog = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    event.preventDefault()
    event.stopPropagation()
    logEvent?.(SynchronizationEvents.CLICKED_IMPORT, {
      offererId: offererId,
      venueId: venueId,
      providerId: providerId,
    })
    setIsConfirmDialogOpened(true)
  }

  const handleCloseConfirmDialog = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    setIsConfirmDialogOpened(false)
  }

  const handleFormSubmit = () => {
    setIsCheckingApi(true)

    const payload: PayloadProps = {
      providerId,
      venueIdAtOfferProvider: siret,
      venueId,
    }

    const isSuccess = saveVenueProvider(payload)
    logEvent?.(SynchronizationEvents.CLICKED_VALIDATE_IMPORT, {
      offererId: offererId,
      venueId: venueId,
      providerId: providerId,
      saved: isSuccess,
    })
    setIsConfirmDialogOpened(false)
  }

  if (isCheckingApi) {
    return <Spinner message="Vérification de votre rattachement" />
  }

  return (
    <>
      <div className={styles['stocks-provider-form']}>
        {!hasApiKey && (
          <div className={styles['account-section']}>
            <div>Compte</div>
            <div>{siret}</div>
          </div>
        )}
        <Button
          variant={ButtonVariant.PRIMARY}
          onClick={handleOpenConfirmDialog}
        >
          Lancer la synchronisation
        </Button>
      </div>
      {isConfirmDialogOpened && (
        <ConfirmDialog
          cancelText="Annuler"
          confirmText="Continuer"
          onCancel={handleCloseConfirmDialog}
          onConfirm={handleFormSubmit}
          title="Demander la synchronisation par API avec un logiciel tiers ?"
          icon={strokeConnectIcon}
        >
          <p>
            En sélectionnant un logiciel, vous l’autorisez à créer des offres
            automatiquement et/ou à gérer les réservations. Chaque
            synchronisation par API est spécifique et dépend de l’intégration
            développée par l’éditeur du logiciel.
          </p>
          <ButtonLink
            className={styles['aide-stock-button']}
            icon={fullLinkIcon}
            link={{
              isExternal: true,
              to: 'https://aide.passculture.app/hc/fr/articles/10616916478236',
              target: '_blank',
              'aria-label': 'Nouvelle fenêtre',
            }}
            variant={ButtonVariant.QUATERNARY}
          >
            Visitez notre FAQ pour plus d’informations
          </ButtonLink>
        </ConfirmDialog>
      )}
    </>
  )
}

export default StocksProviderForm
