import { api } from 'apiClient/api'

type PublishCollectiveOfferAdapter = Adapter<string, null, null>

const publishCollectiveOfferAdapter: PublishCollectiveOfferAdapter =
  async offerId => {
    try {
      await api.patchCollectiveOfferPublication(offerId)
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

export default publishCollectiveOfferAdapter
