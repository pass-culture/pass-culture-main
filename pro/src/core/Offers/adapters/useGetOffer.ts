import { IApiOfferIndividual, IOfferIndividual } from 'core/Offers/types'

import { apiV1 } from 'api/api'
import { serializeOfferApi } from './serializers'
import { useAdapter } from 'hooks'

type GetOfferAdapter = Adapter<string, IOfferIndividual, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
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

const useGetOfferIndividual = (offerId?: string) => {
  const responseFailure: AdapterFailure<null> = {
    payload: null,
    isOk: false,
    message: 'Une erreur est survenue lors de la récupération de votre offre',
  }

  return useAdapter<IOfferIndividual, null>(() => {
    if (offerId === undefined) {
      return Promise.resolve(responseFailure)
    }
    return getOfferAdapter(offerId)
  })
}

export default useGetOfferIndividual
