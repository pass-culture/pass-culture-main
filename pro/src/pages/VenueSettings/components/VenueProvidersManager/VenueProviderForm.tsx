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
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { GenericCinemaProviderForm } from './GenericCinemaProviderForm/GenericCinemaProviderForm'
import { StocksProviderForm } from './StocksProviderForm/StocksProviderForm'

interface VenueProviderFormProps {
  afterSubmit: () => Promise<void>
  provider: ProviderResponse
  venue: GetVenueResponseModel
  providerSelectRef?: React.RefObject<HTMLSelectElement>
  selectSoftwareButtonRef?: React.RefObject<HTMLButtonElement>
}

export const VenueProviderForm = ({
  afterSubmit,
  provider,
  venue,
  providerSelectRef,
  selectSoftwareButtonRef,
}: VenueProviderFormProps) => {
  const snackBar = useSnackBar()
  const createVenueProvider = async (
    payload: PostVenueProviderBody
  ): Promise<boolean> => {
    try {
      await api.createVenueProvider(payload)

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

  return shouldDisplayCinemaDrawer ? (
    <DialogBuilder
      variant="drawer"
      title="Modifier les paramètres de vos offres"
      defaultOpen
      refToFocusOnClose={providerSelectRef}
    >
      <GenericCinemaProviderForm
        isCreatedEntity
        showAdvancedFields={isAllocineProvider(provider)}
        providerId={Number(provider.id)}
        saveVenueProvider={createVenueProvider}
        venueId={venue.id}
        offererId={venue.managingOfferer.id}
      />
    </DialogBuilder>
  ) : (
    <StocksProviderForm
      providerId={Number(provider.id)}
      saveVenueProvider={createVenueProvider}
      siret={venue.siret}
      venueId={venue.id}
      hasOffererProvider={provider.hasOffererProvider}
      offererId={venue.managingOfferer.id}
    />
  )
}
