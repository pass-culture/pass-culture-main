import * as pcapi from '../../../../repository/pcapi/pcapi'
import { GET_DATA_ERROR_MESSAGE } from '../../../shared'
import { Providers } from '../../types'

import { serializeProvidersApi } from './serializers'

type GetProvidersAdapter = Adapter<number | undefined, Providers[], Providers[]>

const FAILING_RESPONSE: AdapterFailure<Providers[]> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getProvidersAdapter: GetProvidersAdapter = async venueId => {
  if (!venueId) {
    return FAILING_RESPONSE
  }
  try {
    const providersResponse = await pcapi.loadProviders(venueId)

    return {
      isOk: true,
      message: '',
      payload: serializeProvidersApi(providersResponse),
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getProvidersAdapter
