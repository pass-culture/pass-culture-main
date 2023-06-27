import { api } from 'apiClient/api'

import { Offerer } from '../types'

import { serializeOffererApi } from './serializers'

type GetOffererAdapter = Adapter<number | undefined, Offerer, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre structure',
  payload: null,
}

const getOffererAdapter: GetOffererAdapter = async offererId => {
  if (offererId === undefined) {
    return FAILING_RESPONSE
  }

  try {
    const venueApi = await api.getOfferer(offererId)

    return {
      isOk: true,
      message: '',
      payload: serializeOffererApi(venueApi),
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getOffererAdapter
