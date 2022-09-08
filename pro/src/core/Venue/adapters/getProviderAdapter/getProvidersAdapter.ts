import * as pcapi from '../../../../repository/pcapi/pcapi'
import { GET_DATA_ERROR_MESSAGE } from '../../../shared'
import { IProviders } from '../../types'

import { serializeProvidersApi } from './serializers'

export type GetProvidersAdapter = Adapter<
  string | undefined,
  IProviders[],
  IProviders[]
>

const FAILING_RESPONSE: AdapterFailure<IProviders[]> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getProvidersAdapter: GetProvidersAdapter = async venueId => {
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
