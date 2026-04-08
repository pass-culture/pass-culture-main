import type { ListOffersQueryModel } from '@/apiClient/v1/new'
import type { SearchListParams } from '@/commons/core/Offers/types'

export const serializeApiIndividualFilters = (
  searchFilters: ListOffersQueryModel & SearchListParams
): ListOffersQueryModel => {
  const { format: _format, page: _page, ...params } = searchFilters

  return {
    ...params,
    categoryId: searchFilters.categoryId,
    creationMode: searchFilters.creationMode,
    offererAddressId: searchFilters.offererAddressId
      ? Number(searchFilters.offererAddressId)
      : undefined,
    offererId: searchFilters.offererId
      ? Number(searchFilters.offererId)
      : undefined,
    status: searchFilters.status,
    venueId: searchFilters.venueId ? Number(searchFilters.venueId) : undefined,
  }
}
