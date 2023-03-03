import { api } from 'apiClient/api'
import { VenueOfOffererFromSiretResponseModel } from 'apiClient/v1'

import { GET_DATA_ERROR_MESSAGE } from '../../../shared'

export type GetVenueOfOffererProvidersAdapter = Adapter<
  string,
  VenueOfOffererFromSiretResponseModel[],
  VenueOfOffererFromSiretResponseModel[]
>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getVenuesOfOffererFromSiretAdapter: GetVenueOfOffererProvidersAdapter =
  async siret => {
    try {
      const venueOfOffererProvidersResponse =
        await api.getVenuesOfOffererFromSiret(siret)
      return {
        isOk: true,
        message: '',
        payload: venueOfOffererProvidersResponse.venues,
      }
    } catch (error) {
      return FAILING_RESPONSE
    }
  }

export default getVenuesOfOffererFromSiretAdapter
