import { api } from 'apiClient/api'
import { GetVenuesOfOffererFromSiretResponseModel } from 'apiClient/v1'

import { GET_DATA_ERROR_MESSAGE } from '../../../shared'

type GetVenueOfOffererProvidersAdapter = Adapter<
  string,
  GetVenuesOfOffererFromSiretResponseModel,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: null,
}

const getVenuesOfOffererFromSiretAdapter: GetVenueOfOffererProvidersAdapter =
  async siret => {
    try {
      const venueOfOffererProvidersResponse =
        await api.getVenuesOfOffererFromSiret(siret)

      return {
        isOk: true,
        message: '',
        payload: venueOfOffererProvidersResponse,
      }
    } catch (error) {
      return FAILING_RESPONSE
    }
  }

export default getVenuesOfOffererFromSiretAdapter
