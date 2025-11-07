import { type ListOffersQueryModel, OfferStatus } from '@/apiClient/v1'
import { nullifyEmptyProps } from '@/commons/utils/nullifyEmptyProps'
import { toEnumOrNull } from '@/commons/utils/toEnumOrNull'
import { toNumberOrNull } from '@/commons/utils/toNumberOrNull'

import type { IndividualSearchFiltersParams } from '../types'

export const serializeApiIndividualFilters = (
  searchFilters: Partial<IndividualSearchFiltersParams>
): Omit<ListOffersQueryModel, 'collectiveOfferType'> => {
  const { format: _format, page: _page, ...params } = searchFilters

  return nullifyEmptyProps({
    ...params,
    categoryId:
      searchFilters.categoryId === 'all' ? null : searchFilters.categoryId,
    creationMode:
      searchFilters.creationMode === 'all' ? null : searchFilters.creationMode,
    offererAddressId: toNumberOrNull(searchFilters.offererAddressId),
    offererId: toNumberOrNull(searchFilters.offererId),
    status: toEnumOrNull(searchFilters.status, OfferStatus),
    venueId: toNumberOrNull(searchFilters.venueId),
  })
}
