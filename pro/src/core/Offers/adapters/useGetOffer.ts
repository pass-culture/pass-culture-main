import { api } from 'apiClient/api'
import { IOfferIndividual } from 'core/Offers/types'
import { useAdapter } from 'hooks'

import { serializeOfferApi } from './serializers'

type GetOfferAdapter = Adapter<string | undefined, IOfferIndividual, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getOfferAdapter: GetOfferAdapter = async offerId => {
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

const useGetOfferIndividual = (offerId?: string) =>
  useAdapter<IOfferIndividual, null>(() => getOfferAdapter(offerId))

export default useGetOfferIndividual
