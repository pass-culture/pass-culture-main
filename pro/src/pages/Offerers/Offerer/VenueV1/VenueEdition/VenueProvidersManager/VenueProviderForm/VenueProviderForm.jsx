import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import { isAllocineProvider, isCinemaProvider } from 'core/Providers'
import useNotification from 'hooks/useNotification'

import AllocineProviderForm from '../AllocineProviderForm/AllocineProviderForm'
import { CinemaProviderForm } from '../CinemaProviderForm/CinemaProviderForm'
import StocksProviderForm from '../StocksProviderForm/StocksProviderForm'
import { getRequestErrorStringFromErrors } from '../utils/getRequestErrorStringFromErrors'

const VenueProviderForm = ({ afterSubmit, provider, venue }) => {
  const displayAllocineProviderForm = isAllocineProvider(provider)
  const displayCDSProviderForm = isCinemaProvider(provider)
  const notify = useNotification()
  const createVenueProvider = useCallback(
    payload => {
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
      providerId={provider.id}
      saveVenueProvider={createVenueProvider}
      venueId={venue.nonHumanizedId}
      offererId={venue.managingOfferer.nonHumanizedId}
    />
  ) : displayCDSProviderForm ? (
    <CinemaProviderForm
      isCreatedEntity
      providerId={provider.id}
      saveVenueProvider={createVenueProvider}
      venueId={venue.nonHumanizedId}
      offererId={venue.managingOfferer.nonHumanizedId}
    />
  ) : (
    <StocksProviderForm
      providerId={provider.id}
      saveVenueProvider={createVenueProvider}
      siret={venue.siret}
      venueId={venue.nonHumanizedId}
      hasOffererProvider={provider.hasOffererProvider}
      offererId={venue.managingOfferer.nonHumanizedId}
    />
  )
}

VenueProviderForm.propTypes = {
  afterSubmit: PropTypes.func.isRequired,
  provider: PropTypes.shape().isRequired,
  venue: PropTypes.shape({
    nonHumanizedId: PropTypes.number.isRequired,
    siret: PropTypes.string.isRequired,
  }).isRequired,
}

export default VenueProviderForm
