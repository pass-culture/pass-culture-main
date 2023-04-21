import { api } from 'apiClient/api'
import { CollectiveOfferTemplate } from 'core/OfferEducational'

type PublishCollectiveOfferTemplateAdapter = Adapter<
  number,
  CollectiveOfferTemplate,
  null
>

const publishCollectiveOfferTemplateAdapter: PublishCollectiveOfferTemplateAdapter =
  async offerId => {
    try {
      const offer = await api.patchCollectiveOfferTemplatePublication(offerId)
      return {
        isOk: true,
        message: '',
        payload: { ...offer, isTemplate: true },
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
