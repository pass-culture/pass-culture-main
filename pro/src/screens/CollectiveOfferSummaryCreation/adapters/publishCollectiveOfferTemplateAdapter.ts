import { api } from 'apiClient/api'

type PublishCollectiveOfferTemplateAdapter = Adapter<string, null, null>

const publishCollectiveOfferTemplateAdapter: PublishCollectiveOfferTemplateAdapter =
  async offerId => {
    try {
      await api.patchCollectiveOfferTemplatePublication(offerId)
      return {
        isOk: true,
        message: '',
        payload: null,
      }
    } catch (error) {
      return {
        isOk: false,
        message:
          'Une erreur est survenue lors de la publication de votre offre.',
        payload: null,
      }
    }
  }

export default publishCollectiveOfferTemplateAdapter
