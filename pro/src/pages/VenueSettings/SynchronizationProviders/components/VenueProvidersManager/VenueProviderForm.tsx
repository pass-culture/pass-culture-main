import { useId, useState } from 'react'

import { api } from '@/apiClient/api'
import { getHumanReadableApiError } from '@/apiClient/helpers'
import type {
  GetVenueResponseModel,
  PostVenueProviderBody,
  ProviderResponse,
} from '@/apiClient/v1'
import {
  isAllocineProvider,
  isCinemaProvider,
} from '@/commons/core/Providers/utils/utils'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'

import { GenericCinemaProviderForm } from './GenericCinemaProviderForm/GenericCinemaProviderForm'
import { StocksProviderForm } from './StocksProviderForm/StocksProviderForm'

interface VenueProviderFormProps {
  afterSubmit: () => Promise<void>
  provider: ProviderResponse
  venue: GetVenueResponseModel
  providerSelectRef?: React.RefObject<HTMLSelectElement | null>
  selectSoftwareButtonRef?: React.RefObject<HTMLButtonElement | null>
}

export const VenueProviderForm = ({
  afterSubmit,
  provider,
  venue,
  providerSelectRef,
  selectSoftwareButtonRef,
}: VenueProviderFormProps) => {
  const [isCinemaModalOpen, setIsCinemaModalOpen] = useState(true)
  const cinemaProviderFormId = useId()
  const snackBar = useSnackBar()
  const createVenueProvider = async (
    payload: PostVenueProviderBody
  ): Promise<boolean> => {
    if (shouldDisplayCinemaDrawer) {
      closeCinemaModal()
    }

    try {
      await api.createVenueProvider({
        path: { venue_id: Number(venue.id) },
        body: payload,
      })

      snackBar.success('La synchronisation a bien été initiée.')
      await afterSubmit()
      return true
    } catch (error) {
      snackBar.error(getHumanReadableApiError(error))
      await afterSubmit()
      return false
    } finally {
      selectSoftwareButtonRef?.current?.focus()
    }
  }

  const shouldDisplayCinemaDrawer =
    isAllocineProvider(provider) || isCinemaProvider(provider)

  const closeCinemaModal = () => {
    setIsCinemaModalOpen(false)
    providerSelectRef?.current?.focus()
  }

  return shouldDisplayCinemaDrawer ? (
    <DetailedModal
      isOpen={isCinemaModalOpen}
      onClose={closeCinemaModal}
      title="Paramètres de vos offres"
      primaryAction={
        <Button
          type="submit"
          form={cinemaProviderFormId}
          label="Lancer la synchronisation"
        />
      }
      secondaryAction={
        <Button
          type="button"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          onClick={closeCinemaModal}
          label="Annuler"
        />
      }
      isFooterFixed
    >
      <GenericCinemaProviderForm
        isCreationMode
        showAdvancedFields={isAllocineProvider(provider)}
        providerId={Number(provider.id)}
        saveVenueProvider={createVenueProvider}
        formId={cinemaProviderFormId}
        showFooter={false}
      />
    </DetailedModal>
  ) : (
    <StocksProviderForm
      providerId={Number(provider.id)}
      saveVenueProvider={createVenueProvider}
      siret={venue.siret}
      hasOffererProvider={provider.hasOffererProvider}
    />
  )
}
