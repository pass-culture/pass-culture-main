import type React from 'react'
import { useRef, useState } from 'react'

import type { PostVenueProviderBody } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { SynchronizationEvents } from '@/commons/core/FirebaseEvents/constants'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeConnectIcon from '@/icons/stroke-connect.svg'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './StocksProviderForm.module.scss'

export interface StocksProviderFormProps {
  offererId: number
  providerId: number
  saveVenueProvider: (payload: PostVenueProviderBody) => Promise<boolean>
  siret?: string | null
  venueId: number
  hasOffererProvider: boolean
}

export const StocksProviderForm = ({
  saveVenueProvider,
  providerId,
  siret,
  venueId,
  hasOffererProvider,
  offererId,
}: StocksProviderFormProps) => {
  const { logEvent } = useAnalytics()
  const [isCheckingApi, setIsCheckingApi] = useState(false)
  const [isConfirmDialogOpened, setIsConfirmDialogOpened] = useState(false)

  const startSynchroButtonRef = useRef<HTMLButtonElement>(null)

  const handleOpenConfirmDialog = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    event.preventDefault()
    event.stopPropagation()
    logEvent(SynchronizationEvents.CLICKED_IMPORT, {
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

  const handleFormSubmit = async () => {
    setIsCheckingApi(true)

    const payload: PostVenueProviderBody = {
      providerId,
      venueIdAtOfferProvider: siret ?? undefined,
    }

    const isSuccess = await saveVenueProvider(payload)
    logEvent(SynchronizationEvents.CLICKED_VALIDATE_IMPORT, {
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
      <div
        className={styles['stocks-provider-form']}
        data-testid="stocks-provider-form"
      >
        {!hasOffererProvider && (
          <div className={styles['account-section']}>
            <div>Compte</div>
            <div>{siret}</div>
          </div>
        )}
        <Button
          onClick={handleOpenConfirmDialog}
          ref={startSynchroButtonRef}
          label="Lancer la synchronisation"
        />
      </div>
      <ConfirmDialog
        cancelText="Annuler"
        confirmText="Continuer"
        onCancel={handleCloseConfirmDialog}
        onConfirm={handleFormSubmit}
        title="Demander la synchronisation par API avec un logiciel tiers ?"
        icon={strokeConnectIcon}
        open={isConfirmDialogOpened}
        refToFocusOnClose={startSynchroButtonRef}
      >
        <p>
          En sélectionnant un logiciel, vous l’autorisez à créer des offres
          automatiquement et/ou à gérer les réservations. Chaque synchronisation
          par API est spécifique et dépend de l’intégration développée par
          l’éditeur du logiciel.
        </p>
        <Button
          as="a"
          icon={fullLinkIcon}
          isExternal
          to="https://aide.passculture.app/hc/fr/articles/10616916478236"
          opensInNewTab
          aria-label="Nouvelle fenêtre"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          label="Visitez notre FAQ pour plus d’informations"
        />
      </ConfirmDialog>
    </>
  )
}
