import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import { Offer, SearchFiltersParams } from 'core/Offers/types'
import { serializeApiFilters } from 'core/Offers/utils'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import { serializeOffers } from './serializers'

export type Payload = {
  offers: Offer[]
}

type GetFilteredOffersAdapter = Adapter<SearchFiltersParams, Payload, Payload>

const FAILING_RESPONSE: AdapterFailure<Payload> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: {
    offers: [],
  },
}

export const getFilteredOffersAdapter: GetFilteredOffersAdapter =
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

      const offers = await api.listOffers(
        nameOrIsbn,
        offererId,
        status as OfferStatus,
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
