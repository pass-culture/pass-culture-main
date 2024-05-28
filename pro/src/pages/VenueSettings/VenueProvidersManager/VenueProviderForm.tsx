import React from 'react'

import { api } from 'apiClient/api'
import { getHumanReadableApiError } from 'apiClient/helpers'
import {
  PostVenueProviderBody,
  GetVenueResponseModel,
  ProviderResponse,
} from 'apiClient/v1'
import {
  isAllocineProvider,
  isCinemaProvider,
} from 'core/Providers/utils/utils'
import useNotification from 'hooks/useNotification'

import { AllocineProviderForm } from './AllocineProviderForm/AllocineProviderForm'
import { CinemaProviderForm } from './CinemaProviderForm/CinemaProviderForm'
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
  const displayAllocineProviderForm = isAllocineProvider(provider)
  const displayCDSProviderForm = isCinemaProvider(provider)
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

  return displayAllocineProviderForm ? (
    <AllocineProviderForm
      isCreatedEntity
      providerId={Number(provider.id)}
      saveVenueProvider={createVenueProvider}
      venueId={venue.id}
      offererId={venue.managingOfferer.id}
    />
  ) : displayCDSProviderForm ? (
    <CinemaProviderForm
      isCreatedEntity
      providerId={Number(provider.id)}
      saveVenueProvider={createVenueProvider}
      venueId={venue.id}
      offererId={venue.managingOfferer.id}
    />
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
