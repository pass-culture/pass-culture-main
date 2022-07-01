import { TUseAdapterFailure, useAdapter } from 'hooks'

import { IOfferIndividual } from 'core/Offers/types'
import { api } from 'apiClient/api'
import { serializeOfferApi } from './serializers'

type GetOfferAdapter = Adapter<string, IOfferIndividual, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getOfferAdapter: GetOfferAdapter = async offerId => {
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

const useGetOfferIndividual = (offerId?: string) => {
  if (offerId === undefined) {
    const responseFailure: TUseAdapterFailure<null> = {
      data: undefined,
      isLoading: false,
      error: {
        message:
          'Une erreur est survenue lors de la récupération de votre offre',
        payload: null,
      },
    }
    return responseFailure
  }

  return useAdapter<IOfferIndividual, null>(() => getOfferAdapter(offerId))
}

export default useGetOfferIndividual
