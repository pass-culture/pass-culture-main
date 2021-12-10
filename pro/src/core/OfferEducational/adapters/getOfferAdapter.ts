import { Offer } from 'custom_types/offer'
import * as pcapi from 'repository/pcapi/pcapi'

type IPayloadSuccess = { offer: Offer }
type IPayloadFailure = { offer: null }
type GetOfferAdapter = Adapter<string, IPayloadSuccess, IPayloadFailure>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: {
    offer: null,
  },
}

export const getOfferAdapter: GetOfferAdapter = async offerId => {
  try {
    const offer = (await pcapi.loadOffer(offerId)) as Offer

    return {
      isOk: true,
      message: '',
      payload: {
        offer,
      },
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}
