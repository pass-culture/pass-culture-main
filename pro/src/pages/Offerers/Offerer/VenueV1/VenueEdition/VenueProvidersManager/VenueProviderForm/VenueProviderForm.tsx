import React, { useCallback } from 'react'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import { PostVenueProviderBody, VenueProviderResponse } from 'apiClient/v1'
import { isAllocineProvider, isCinemaProvider } from 'core/Providers'
import { IVenue } from 'core/Venue'
import { IProviders } from 'core/Venue/types'
import useNotification from 'hooks/useNotification'

import AllocineProviderForm from '../AllocineProviderForm/AllocineProviderForm'
import { CinemaProviderForm } from '../CinemaProviderForm/CinemaProviderForm'
import StocksProviderForm from '../StocksProviderForm/StocksProviderForm'
import { getRequestErrorStringFromErrors } from '../utils/getRequestErrorStringFromErrors'

interface VenueProviderFormProps {
  afterSubmit: (createdVenueProvider?: VenueProviderResponse) => void
  provider: IProviders
  venue: IVenue
}

const VenueProviderForm = ({
  afterSubmit,
  provider,
  venue,
}: VenueProviderFormProps) => {
  const displayAllocineProviderForm = isAllocineProvider(provider)
  const displayCDSProviderForm = isCinemaProvider(provider)
  const notify = useNotification()
  const createVenueProvider = useCallback(
    (payload?: PostVenueProviderBody) => {
      api
        .createVenueProvider(payload)
        .then(createdVenueProvider => {
          notify.success('La synchronisation a bien été initiée.')
          afterSubmit(createdVenueProvider)
        })
        .catch(error => {
          if (isErrorAPIError(error)) {
            notify.error(getRequestErrorStringFromErrors(getError(error)))
            afterSubmit()
          }
        })
    },
    [afterSubmit]
  )

  return displayAllocineProviderForm ? (
    <AllocineProviderForm
      isCreatedEntity
      providerId={Number(provider.id)}
      saveVenueProvider={createVenueProvider}
      venueId={venue.nonHumanizedId}
      offererId={venue.managingOfferer.nonHumanizedId}
    />
  ) : displayCDSProviderForm ? (
    <CinemaProviderForm
      isCreatedEntity
      providerId={Number(provider.id)}
      saveVenueProvider={createVenueProvider}
      venueId={venue.nonHumanizedId}
      offererId={venue.managingOfferer.nonHumanizedId}
    />
  ) : (
    <StocksProviderForm
      providerId={Number(provider.id)}
      saveVenueProvider={createVenueProvider}
      siret={venue.siret}
      venueId={venue.nonHumanizedId}
      hasOffererProvider={provider.hasOffererProvider}
      offererId={venue.managingOfferer.nonHumanizedId}
    />
  )
}

export default VenueProviderForm
