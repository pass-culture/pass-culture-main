import type { ListOffersQueryModel } from '@/apiClient/v1/new'

import type { SearchListParams } from '../types'

/**
 * Strips the frontend-only `format` and `page` fields from the merged
 * filter shape so what is sent to the backend matches `ListOffersQueryModel`.
 */
export const serializeApiIndividualFilters = (
  searchFilters: ListOffersQueryModel & SearchListParams
): ListOffersQueryModel => {
  const { format: _format, page: _page, ...query } = searchFilters

  return query
}
