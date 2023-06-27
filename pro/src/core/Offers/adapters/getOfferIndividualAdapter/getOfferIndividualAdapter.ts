import { api } from 'apiClient/api'
import { OfferIndividual } from 'core/Offers/types'

import { serializeOfferApi } from './serializers'

type GetOfferIndividualAdapter = Adapter<
  number | undefined,
  OfferIndividual,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getOfferIndividualAdapter: GetOfferIndividualAdapter = async offerId => {
  if (offerId === undefined) {
    return FAILING_RESPONSE
  }

  try {
    const offerApi = await api.getOffer(offerId)

    return {
      isOk: true,
      message: '',
      payload: serializeOfferApi(offerApi),
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getOfferIndividualAdapter
