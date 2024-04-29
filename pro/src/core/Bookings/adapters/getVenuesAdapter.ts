import { api } from 'apiClient/api'
import { GetVenuesAdapter, VenuesPayload } from 'core/Bookings/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { formatAndOrderVenues } from 'repository/venuesService'

const FAILING_RESPONSE: AdapterFailure<VenuesPayload> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: { venues: [] },
}

const getVenuesAdapter: GetVenuesAdapter = async () => {
  try {
    const venuesForOfferer = await api.getVenues(undefined, false, undefined)

    return {
      isOk: true,
      message: null,
      payload: {
        venues: formatAndOrderVenues(venuesForOfferer.venues),
      },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getVenuesAdapter
