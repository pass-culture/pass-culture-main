import type { ListOffersQueryModel } from '@/apiClient/v1/new'
import type { IndividualOffersFilters } from '@/pages/IndividualOffers/common/types'

export const serializeApiIndividualFilters = (
  searchFilters: IndividualOffersFilters
): ListOffersQueryModel => {
  const { page: _page, ...query } = searchFilters

  return query
}
