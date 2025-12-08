import {
  GET_COLLECTIVE_OFFERS_BOOKABLE_QUERY_KEY,
  GET_COLLECTIVE_OFFERS_TEMPLATE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'

import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '../constants'
import type { CollectiveSearchFiltersParams } from '../types'

export type GetCollectiveOffersSwrKeysProps = {
  isInTemplateOffersPage: boolean
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>
  selectedOffererId: number
  selectedVenueId?: number
}

//  Make sure that the exact same query key is used across collective offers list actions
export function getCollectiveOffersSwrKeys({
  isInTemplateOffersPage,
  urlSearchFilters,
  selectedOffererId,
  selectedVenueId,
}: GetCollectiveOffersSwrKeysProps): [string, CollectiveSearchFiltersParams] {
  const collectiveOffersListQueryKey = isInTemplateOffersPage
    ? GET_COLLECTIVE_OFFERS_TEMPLATE_QUERY_KEY
    : GET_COLLECTIVE_OFFERS_BOOKABLE_QUERY_KEY

  const apiFilters: CollectiveSearchFiltersParams = {
    ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    ...urlSearchFilters,
    ...{ offererId: selectedOffererId.toString() },
    ...{ venueId: selectedVenueId?.toString() ?? 'all' },
    page: undefined,
  }

  return [collectiveOffersListQueryKey, apiFilters]
}
