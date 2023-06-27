import { api } from 'apiClient/api'

type SuccessPayload = null
type FailurePayload = null
type PublishIndividualOffer = Adapter<
  { offerId: number },
  SuccessPayload,
  FailurePayload
>

const publishIndividualOffer: PublishIndividualOffer = async ({ offerId }) => {
  try {
    await api.patchPublishOffer({ id: offerId })
    return {
      isOk: true,
      message: '',
      payload: null,
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
