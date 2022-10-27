import { api } from 'apiClient/api'
import { VenueProviderResponse } from 'apiClient/v1'

import { GET_DATA_ERROR_MESSAGE } from '../../../shared'

export type GetVenueProvidersAdapter = Adapter<
  string | undefined,
  VenueProviderResponse[],
  VenueProviderResponse[]
>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getVenueProvidersAdapter: GetVenueProvidersAdapter = async venueId => {
  try {
    // @ts-expect-error string is not assignable to type number
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
