import { api } from 'apiClient/api'
import { GetCollectiveOfferResponseModel } from 'apiClient/v1'

type PayloadFailure = null
type GetCollectiveOfferAdapter = Adapter<
  number,
  GetCollectiveOfferResponseModel,
  PayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<PayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getCollectiveOfferAdapter: GetCollectiveOfferAdapter = async (
  offerId
) => {
  try {
    const offer = await api.getCollectiveOffer(offerId)

    return {
      isOk: true,
      message: '',
      payload: { ...offer, isTemplate: false },
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getCollectiveOfferAdapter
