import { Adapter, AdapterFailure } from 'app/types'
import { OfferType } from 'app/types/offers'
import * as pcapi from 'repository/pcapi/pcapi'

type GetCollectiveOfferAdapter = Adapter<number | string, OfferType, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: null,
}

export const getCollectiveOfferAdapter: GetCollectiveOfferAdapter =
  async offerId => {
    try {
      const result = await pcapi.getCollectiveOffer(offerId)

      return {
        isOk: true,
        message: null,
        payload: {
          ...result,
          stocks: [result.stock],
          extraData: {
            students: result.students,
            offerVenue: result.offerVenue,
            isShowcase: false,
            contactEmail: result.contactEmail,
            contactPhone: result.contactPhone,
          },
        },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
