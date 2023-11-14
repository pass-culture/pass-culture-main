import { api } from 'apiClient/api'
import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { Offer, SearchFiltersParams } from 'core/Offers/types'
import { serializeApiFilters } from 'core/Offers/utils'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import { serializeOffers } from './serializers'

type Payload = {
  offers: Offer[]
}

type GetFilteredCollectiveOffersAdapter = Adapter<
  SearchFiltersParams,
  Payload,
  Payload
>

const FAILING_RESPONSE: AdapterFailure<Payload> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: {
    offers: [],
  },
}

const getFilteredCollectiveOffersAdapter: GetFilteredCollectiveOffersAdapter =
  async (apiFilters) => {
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
        collectiveOfferType,
        format,
      } = serializeApiFilters(apiFilters)

      const offers = await api.getCollectiveOffers(
        nameOrIsbn,
        offererId,
        status as CollectiveOfferDisplayedStatus,
        venueId,
        categoryId,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        collectiveOfferType,
        format
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
