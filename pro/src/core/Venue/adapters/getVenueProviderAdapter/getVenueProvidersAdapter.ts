import { api } from 'apiClient/api'
import { VenueProviderResponse } from 'apiClient/v1'

import { GET_DATA_ERROR_MESSAGE } from '../../../shared'

type GetVenueProvidersAdapter = Adapter<
  number | undefined,
  VenueProviderResponse[],
  VenueProviderResponse[]
>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getVenueProvidersAdapter: GetVenueProvidersAdapter = async venueId => {
  if (!venueId) {
    return FAILING_RESPONSE
  }
  try {
    const venueProvidersResponse = await api.listVenueProviders(venueId)
    return {
      isOk: true,
      message: '',
      payload: venueProvidersResponse.venue_providers,
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getVenueProvidersAdapter
