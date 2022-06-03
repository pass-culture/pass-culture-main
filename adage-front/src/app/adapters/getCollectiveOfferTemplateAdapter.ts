import { api } from 'api/api'
import { Adapter, AdapterFailure } from 'app/types'
import { OfferType } from 'app/types/offers'

type GetCollectiveOfferTemplateAdapter = Adapter<number, OfferType, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: null,
}

export const getCollectiveOfferTemplateAdapter: GetCollectiveOfferTemplateAdapter =
  async offerId => {
    try {
      const result = await api.getAdageIframeGetCollectiveOffer(offerId)

      return {
        isOk: true,
        message: null,
        payload: {
          ...result,
          stocks: [
            // False stock to satisfy ts
            {
              educationalPriceDetail: result.educationalPriceDetail,
              beginningDatetime: new Date('2030-01-01').toISOString(),
              numberOfTickets: undefined,
              price: 0,
              id: 0,
              isBookable: false,
              bookingLimitDatetime: new Date('2030-01-01').toISOString(),
            },
          ],
          extraData: {
            students: result.students,
            offerVenue: result.offerVenue,
            isShowcase: true,
            contactEmail: result.contactEmail,
            contactPhone: result.contactPhone,
          },
        },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
