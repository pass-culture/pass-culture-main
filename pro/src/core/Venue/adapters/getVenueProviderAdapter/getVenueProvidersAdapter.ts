import { VenueProviderResponse } from 'apiClient/v1'
import * as pcapi from 'repository/pcapi/pcapi'

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
    const venueProvidersResponse = await pcapi.loadVenueProviders(venueId)
    return {
      isOk: true,
      message: '',
      payload: venueProvidersResponse,
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getVenueProvidersAdapter
