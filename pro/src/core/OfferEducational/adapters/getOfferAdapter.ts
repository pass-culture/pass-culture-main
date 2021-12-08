import { Offer } from 'custom_types/offer'
import * as pcapi from 'repository/pcapi/pcapi'

type GetOfferAdapter = Adapter<string, { offer: Offer | null }>

const FAILING_RESPONSE = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: {
    offer: null,
  },
}

const getOfferAdapter: GetOfferAdapter = async offerId => {
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

export default getOfferAdapter
