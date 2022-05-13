import * as pcapi from 'repository/pcapi/pcapi'

import { GetVenuesAdapter, VenuesPayload } from 'core/Bookings'

import { formatAndOrderVenues } from 'repository/venuesService'

const FAILING_RESPONSE: AdapterFailure<VenuesPayload> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
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
