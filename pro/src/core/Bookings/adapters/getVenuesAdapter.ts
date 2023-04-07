import { api } from 'apiClient/api'
import { GetVenuesAdapter, VenuesPayload } from 'core/Bookings'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { legacylegacyformatAndOrderVenues } from 'repository/venuesService'

const FAILING_RESPONSE: AdapterFailure<VenuesPayload> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: { venues: [] },
}

export const getVenuesAdapter: GetVenuesAdapter = async () => {
  try {
    const venuesForOfferer = await api.getVenues(
      true,
      undefined,
      false,
      undefined
    )

    return {
      isOk: true,
      message: null,
      payload: {
        venues: legacylegacyformatAndOrderVenues(venuesForOfferer.venues),
      },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getVenuesAdapter
