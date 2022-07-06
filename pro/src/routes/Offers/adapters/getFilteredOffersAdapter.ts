import { Offer, TSearchFilters } from 'core/Offers/types'

import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { api } from 'api/v1/api'
import { serializeApiFilters } from 'core/Offers/utils'
import { serializeOffers } from './serializers'

type IPayload = {
  offers: Offer[]
}

type GetFilteredOffersAdapter = Adapter<TSearchFilters, IPayload, IPayload>

const FAILING_RESPONSE: AdapterFailure<IPayload> = {
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

      const offers = await api.getOffersListOffers(
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

export default getFilteredOffersAdapter
