import { api } from 'apiClient/api'
import { IndividualOffer } from 'core/Offers/types'

type GetIndividualOfferAdapter = Adapter<
  number | undefined,
  IndividualOffer,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getIndividualOfferAdapter: GetIndividualOfferAdapter = async (
  offerId
) => {
  if (offerId === undefined) {
    return FAILING_RESPONSE
  }

  try {
    const offerApi = await api.getOffer(offerId)

    return {
      isOk: true,
      message: '',
      payload: offerApi,
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getIndividualOfferAdapter
