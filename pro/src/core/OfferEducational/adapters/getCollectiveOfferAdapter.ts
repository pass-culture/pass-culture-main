import { api } from 'apiClient/api'
import { GetCollectiveOfferResponseModel } from 'apiClient/v1'

type IPayloadFailure = null
type GetCollectiveOfferAdapter = Adapter<
  string,
  GetCollectiveOfferResponseModel,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getCollectiveOfferAdapter: GetCollectiveOfferAdapter = async offerId => {
  try {
    const offer = await api.getCollectiveOffer(offerId)

    return {
      isOk: true,
      message: '',
      payload: offer,
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getCollectiveOfferAdapter
