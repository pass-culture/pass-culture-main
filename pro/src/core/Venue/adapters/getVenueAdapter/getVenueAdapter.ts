import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'

type GetVenueAdapter = Adapter<number | undefined, GetVenueResponseModel, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre lieu',
  payload: null,
}

const getVenueAdapter: GetVenueAdapter = async (venueId) => {
  if (venueId === undefined) {
    return FAILING_RESPONSE
  }

  try {
    const venueApi = await api.getVenue(venueId)

    return {
      isOk: true,
      message: '',
      payload: venueApi,
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getVenueAdapter
