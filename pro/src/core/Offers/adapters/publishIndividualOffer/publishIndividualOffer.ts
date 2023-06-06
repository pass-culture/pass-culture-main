import { api } from 'apiClient/api'

type TSuccessPayload = null
type TFailurePayload = null
type TPublishIndividualOffer = Adapter<
  { offerId: number },
  TSuccessPayload,
  TFailurePayload
>

const publishIndividualOffer: TPublishIndividualOffer = async ({ offerId }) => {
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
