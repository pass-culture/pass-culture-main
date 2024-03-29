import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'

type GetOffererAdapter = Adapter<
  number | undefined,
  GetOffererResponseModel,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre structure',
  payload: null,
}

const getOffererAdapter: GetOffererAdapter = async (offererId) => {
  if (offererId === undefined) {
    return FAILING_RESPONSE
  }

  try {
    const venueApi = await api.getOfferer(offererId)

    return {
      isOk: true,
      message: '',
      payload: venueApi,
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getOffererAdapter
