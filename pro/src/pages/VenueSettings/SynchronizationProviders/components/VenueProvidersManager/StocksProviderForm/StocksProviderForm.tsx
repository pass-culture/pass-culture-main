import type React from 'react'
import { useState } from 'react'

import type { PostVenueProviderBody } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { SynchronizationEvents } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import strokeConnectIcon from '@/icons/stroke-connect.svg'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './StocksProviderForm.module.scss'

export interface StocksProviderFormProps {
  providerId: number
  saveVenueProvider: (payload: PostVenueProviderBody) => Promise<boolean>
  siret?: string | null
  hasOffererProvider: boolean
}

export const StocksProviderForm = ({
  saveVenueProvider,
  providerId,
  siret,
  hasOffererProvider,
}: StocksProviderFormProps) => {
  const { logEvent } = useAnalytics()
  const [isCheckingApi, setIsCheckingApi] = useState(false)
  const [isConfirmDialogOpened, setIsConfirmDialogOpened] = useState(false)

  const handleOpenConfirmDialog = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    event.preventDefault()
    event.stopPropagation()
    logEvent(SynchronizationEvents.CLICKED_IMPORT, {
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
          label="Lancer la synchronisation"
        />
      </div>
      <SimpleModal
        title="Demander la synchronisation par API avec un logiciel tiers ?"
        iconPath={strokeConnectIcon}
        isOpen={isConfirmDialogOpened}
        onClose={handleCloseConfirmDialog}
        actionButtons={
          <>
            <Button
              onClick={handleCloseConfirmDialog}
              variant={ButtonVariant.SECONDARY}
              label="Annuler"
            />
            <Button onClick={handleFormSubmit} label="Continuer" />
          </>
        }
      >
        <p>
          En sélectionnant un logiciel, vous l’autorisez à créer des offres
          automatiquement et/ou à gérer les réservations. Chaque synchronisation
          par API est spécifique et dépend de l’intégration développée par
          l’éditeur du logiciel.
        </p>
        <Button
          as="a"
          to="https://aide.passculture.app/hc/fr/articles/10616916478236"
          opensInNewTab
          aria-label="Nouvelle fenêtre"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          label="Visitez notre FAQ pour plus d’informations"
        />
      </SimpleModal>
    </>
  )
}
