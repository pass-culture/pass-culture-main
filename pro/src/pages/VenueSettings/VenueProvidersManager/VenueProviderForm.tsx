import { api } from 'apiClient/api'
import { getHumanReadableApiError } from 'apiClient/helpers'
import {
  GetVenueResponseModel,
  PostVenueProviderBody,
  ProviderResponse,
} from 'apiClient/v1'
import {
  isAllocineProvider,
  isCinemaProvider,
} from 'commons/core/Providers/utils/utils'
import { useNotification } from 'commons/hooks/useNotification'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import { GenericCinemaProviderForm } from './GenericCinemaProviderForm/GenericCinemaProviderForm'
import { StocksProviderForm } from './StocksProviderForm/StocksProviderForm'

interface VenueProviderFormProps {
  afterSubmit: () => Promise<void>
  provider: ProviderResponse
  venue: GetVenueResponseModel
}

export const VenueProviderForm = ({
  afterSubmit,
  provider,
  venue,
}: VenueProviderFormProps) => {
  const notify = useNotification()
  const createVenueProvider = async (
    payload?: PostVenueProviderBody
  ): Promise<boolean> => {
    try {
      await api.createVenueProvider(payload)

      notify.success('La synchronisation a bien été initiée.')
      await afterSubmit()
      return true
    } catch (error) {
      notify.error(getHumanReadableApiError(error))
      await afterSubmit()
      return false
    }
  }

  const shouldDisplayCinemaDrawer =
    isAllocineProvider(provider) || isCinemaProvider(provider)

  return shouldDisplayCinemaDrawer ? (
    <DialogBuilder
      variant="drawer"
      title="Modifier les paramètres de vos offres"
      defaultOpen={shouldDisplayCinemaDrawer}
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
