import { api } from 'apiClient/api'

type IPayloadFailure = null
type DeleteCollectiveOfferImageAdapter = Adapter<string, null, IPayloadFailure>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message:
    "Une erreur est survenue lors de la suppression de l'image de l'offre",
  payload: null,
}

const deleteCollectiveOfferTemplateImageAdapter: DeleteCollectiveOfferImageAdapter =
  async offerId => {
    try {
      await api.deleteOfferTemplateImage(offerId)

      return {
        isOk: true,
        message: '',
        payload: null,
      }
    } catch (error) {
      return FAILING_RESPONSE
    }
  }

export default deleteCollectiveOfferTemplateImageAdapter
