import { api } from 'api/api'
import { Offerer } from 'core/Offers/types'

type IPayload = Offerer

type GetOffererAdapter = Adapter<string, IPayload, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: null,
}

export const getOffererAdapter: GetOffererAdapter = async (
  offererId: string
) => {
  try {
    const offerer = await api.getOfferersGetOfferer(offererId)

    return {
      isOk: true,
      message: null,
      payload: {
        id: offerer.id,
        name: offerer.name,
      },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getOffererAdapter
