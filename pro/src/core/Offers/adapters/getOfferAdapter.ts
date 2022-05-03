import { apiV1 } from 'api/api'
import { IApiOfferIndividual, IOfferIndividual } from 'core/Offers/types'

import { serializeOfferApi } from './serializers'

type IPayloadFailure = null
type GetOfferAdapter = Adapter<string, IOfferIndividual, IPayloadFailure>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getOfferAdapter: GetOfferAdapter = async offerId => {
  try {
    const offerApi = (await apiV1.getOffersGetOffer(
      offerId
    )) as IApiOfferIndividual

    return {
      isOk: true,
      message: '',
      payload: serializeOfferApi(offerApi),
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getOfferAdapter
