import { api } from 'apiClient/api'
import { GetCollectiveOfferResponseModel } from 'apiClient/v1'

type PublishCollectiveOfferAdapter = Adapter<
  number,
  GetCollectiveOfferResponseModel,
  null
>

const publishCollectiveOfferAdapter: PublishCollectiveOfferAdapter = async (
  offerId
) => {
  try {
    const offer = await api.patchCollectiveOfferPublication(offerId)
    return {
      isOk: true,
      message: '',
      payload: { ...offer, isTemplate: false },
    }
  } catch (error) {
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la publication de votre offre.',
      payload: null,
    }
  }
}

export default publishCollectiveOfferAdapter
