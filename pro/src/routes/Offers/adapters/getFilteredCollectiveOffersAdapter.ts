import { api } from 'api/v1/api'
import { Offer, TSearchFilters } from 'core/Offers/types'

import { serializeOffers, serializeApiFilters } from './serializers'

type IPayload = {
  offers: Offer[]
}

type GetFilteredCollectiveOffersAdapter = Adapter<
  TSearchFilters,
  IPayload,
  IPayload
>

const FAILING_RESPONSE: AdapterFailure<IPayload> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: {
    offers: [],
  },
}

export const getFilteredCollectiveOffersAdapter: GetFilteredCollectiveOffersAdapter =
  async apiFilters => {
    try {
      const {
        nameOrIsbn,
        offererId,
        venueId,
        categoryId,
        status,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
      } = serializeApiFilters(apiFilters)

      const offers = await api.getCollectiveListCollectiveOffers(
        nameOrIsbn,
        offererId,
        status,
        venueId,
        categoryId,
        creationMode,
        periodBeginningDate,
        periodEndingDate
      )

      return {
        isOk: true,
        message: null,
        payload: {
          offers: serializeOffers(offers),
        },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

export default getFilteredCollectiveOffersAdapter
