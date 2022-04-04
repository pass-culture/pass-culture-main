import * as pcapi from 'repository/pcapi/pcapi'
import { formatAndOrderVenues } from 'repository/venuesService'

type IPayload = { venues: { id: string; displayName: string }[] }

type GetVenuesAdapter = Adapter<void, IPayload, IPayload>

const FAILING_RESPONSE: AdapterFailure<IPayload> = {
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
