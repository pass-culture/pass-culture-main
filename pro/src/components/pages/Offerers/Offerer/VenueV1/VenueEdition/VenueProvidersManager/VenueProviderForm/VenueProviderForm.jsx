import PropTypes from 'prop-types'
import React, { useCallback } from 'react'
import { useDispatch } from 'react-redux'

import { isAllocineProvider, isCinemaProvider } from 'core/Providers'
import * as pcapi from 'repository/pcapi/pcapi'
import { showNotification } from 'store/reducers/notificationReducer'

import AllocineProviderForm from '../AllocineProviderForm/AllocineProviderForm'
import { CinemaProviderForm } from '../CinemaProviderForm/CinemaProviderForm'
import StocksProviderForm from '../StocksProviderForm/StocksProviderForm'
import { getRequestErrorStringFromErrors } from '../utils/getRequestErrorStringFromErrors'

const VenueProviderForm = ({ afterSubmit, provider, venue }) => {
  const displayAllocineProviderForm = isAllocineProvider(provider)
  const displayCDSProviderForm = isCinemaProvider(provider)
  const dispatch = useDispatch()
  const createVenueProvider = useCallback(
    payload => {
      pcapi
        .createVenueProvider(payload)
        .then(createdVenueProvider => {
          dispatch(
            showNotification({
              text: 'La synchronisation a bien été initiée.',
              type: 'success',
            })
          )
          afterSubmit(createdVenueProvider)
        })
        .catch(error => {
          dispatch(
            showNotification({
              text: getRequestErrorStringFromErrors(error.errors),
              type: 'error',
            })
          )
          afterSubmit()
        })
    },
    [afterSubmit, dispatch]
  )

  return displayAllocineProviderForm ? (
    <AllocineProviderForm
      isCreatedEntity
      providerId={provider.id}
      saveVenueProvider={createVenueProvider}
      venueId={venue.id}
    />
  ) : displayCDSProviderForm ? (
    <CinemaProviderForm
      isCreatedEntity
      providerId={provider.id}
      saveVenueProvider={createVenueProvider}
      venueId={venue.id}
    />
  ) : (
    <StocksProviderForm
      providerId={provider.id}
      saveVenueProvider={createVenueProvider}
      siret={venue.siret}
      venueId={venue.id}
    />
  )
}

VenueProviderForm.propTypes = {
  afterSubmit: PropTypes.func.isRequired,
  provider: PropTypes.shape().isRequired,
  venue: PropTypes.shape({
    id: PropTypes.string.isRequired,
    // managingOffererId: PropTypes.string.isRequired,
    siret: PropTypes.string.isRequired,
    // departementCode: PropTypes.string.isRequired,
  }).isRequired,
}

export default VenueProviderForm
