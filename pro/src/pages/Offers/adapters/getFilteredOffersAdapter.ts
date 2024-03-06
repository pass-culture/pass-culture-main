import { api } from 'apiClient/api'
import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { SearchFiltersParams } from 'core/Offers/types'
import { serializeApiFilters } from 'core/Offers/utils'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

type Payload = {
  offers: ListOffersOfferResponseModel[]
}

type GetFilteredOffersAdapter = Adapter<SearchFiltersParams, Payload, Payload>

const FAILING_RESPONSE: AdapterFailure<Payload> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: {
    offers: [],
  },
}

export const getFilteredOffersAdapter: GetFilteredOffersAdapter = async (
  apiFilters
) => {
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
        offers,
      },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}
