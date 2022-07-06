import * as pcapi from 'repository/pcapi/pcapi'

import { GetVenuesAdapter, VenuesPayload } from 'core/Bookings'

import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { formatAndOrderVenues } from 'repository/venuesService'

const FAILING_RESPONSE: AdapterFailure<VenuesPayload> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: { venues: [] },
}

export const getVenuesAdapter: GetVenuesAdapter = async () => {
  try {
    const venuesForOfferer = await pcapi.getVenuesForOfferer()

    return {
      isOk: true,
      message: null,
      payload: { venues: formatAndOrderVenues(venuesForOfferer) },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getVenuesAdapter
