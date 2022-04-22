import { CollectiveOfferTemplate } from 'core/OfferEducational/types'
import * as pcapi from 'repository/pcapi/pcapi'

type IPayloadFailure = null
type GetCollectiveOfferTemplateAdapter = Adapter<
  string,
  CollectiveOfferTemplate,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getCollectiveOfferTemplateAdapter: GetCollectiveOfferTemplateAdapter =
  async offerId => {
    try {
      const offer = await pcapi.getCollectiveOfferTemplate(offerId)

      return {
        isOk: true,
        message: '',
        payload: { ...offer, isBooked: false },
      }
    } catch (error) {
      return FAILING_RESPONSE
    }
  }

export default getCollectiveOfferTemplateAdapter
