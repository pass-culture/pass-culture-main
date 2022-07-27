import { api } from 'apiClient/api'
import { Offer, TSearchFilters } from 'core/Offers/types'
import { serializeApiFilters } from 'core/Offers/utils'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import { serializeOffers } from './serializers'

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
  message: GET_DATA_ERROR_MESSAGE,
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

      const offers = await api.getCollectiveOffers(
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
