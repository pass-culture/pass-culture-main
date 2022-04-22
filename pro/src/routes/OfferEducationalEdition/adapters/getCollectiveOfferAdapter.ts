import { CollectiveOffer } from 'core/OfferEducational/types'
import * as pcapi from 'repository/pcapi/pcapi'

type IPayloadFailure = null
type GetCollectiveOfferAdapter = Adapter<
  string,
  CollectiveOffer,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getCollectiveOfferAdapter: GetCollectiveOfferAdapter = async offerId => {
  try {
    const offer = await pcapi.getCollectiveOffer(offerId)
    const isBooked = offer.collectiveStock.isBooked

    return {
      isOk: true,
      message: '',
      payload: { ...offer, isBooked },
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getCollectiveOfferAdapter
