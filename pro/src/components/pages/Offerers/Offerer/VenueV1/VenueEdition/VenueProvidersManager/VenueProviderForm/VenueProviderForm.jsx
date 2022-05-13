import * as pcapi from 'repository/pcapi/pcapi'

import React, { useCallback } from 'react'

import AllocineProviderForm from '../AllocineProviderForm/AllocineProviderForm'
import PropTypes from 'prop-types'
import StocksProviderForm from '../StocksProviderForm/StocksProviderForm'
import { getRequestErrorStringFromErrors } from '../utils/getRequestErrorStringFromErrors'
import { isAllocineProvider } from 'components/pages/Offers/domain/localProvider'
import { showNotification } from 'store/reducers/notificationReducer'
import { useDispatch } from 'react-redux'

const VenueProviderForm = ({ afterSubmit, provider, venue }) => {
  const displayAllocineProviderForm = isAllocineProvider(provider)
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
