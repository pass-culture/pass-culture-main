import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'

type SuccessPayload = GetIndividualOfferResponseModel
type FailurePayload = null
type PublishIndividualOffer = Adapter<
  { offerId: number },
  SuccessPayload,
  FailurePayload
>

const publishIndividualOffer: PublishIndividualOffer = async ({ offerId }) => {
  try {
    const publishedOffer = await api.patchPublishOffer({ id: offerId })
    return {
      isOk: true,
      message: '',
      payload: publishedOffer,
    }
  } catch (error) {
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la publication de votre offre',
      payload: null,
    }
  }
}

export default publishIndividualOffer
