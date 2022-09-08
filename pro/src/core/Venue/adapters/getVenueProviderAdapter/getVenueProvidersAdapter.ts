import { IVenueProviderApi } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/CinemaProviderItem/types'
import * as pcapi from 'repository/pcapi/pcapi'

import { GET_DATA_ERROR_MESSAGE } from '../../../shared'

import { serializeVenueProvidersApi } from './serializers'

export type GetVenueProvidersAdapter = Adapter<
  string | undefined,
  IVenueProviderApi[],
  IVenueProviderApi[]
>

const FAILING_RESPONSE: AdapterFailure<IVenueProviderApi[]> = {
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
      payload: serializeVenueProvidersApi(venueProvidersResponse),
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getVenueProvidersAdapter
