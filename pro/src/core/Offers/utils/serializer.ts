import { ListOffersQueryModel } from 'apiClient/v1'

import { DEFAULT_SEARCH_FILTERS } from '../constants'
import { TSearchFilters } from '../types'

export const serializeApiFilters = <K extends keyof TSearchFilters>(
  searchFilters: Partial<TSearchFilters> & { page?: number }
): ListOffersQueryModel => {
  const keys = Object.keys(DEFAULT_SEARCH_FILTERS) as K[]

  const body = {} as ListOffersQueryModel

  keys.forEach(field => {
    if (
      searchFilters[field] &&
      searchFilters[field] !== DEFAULT_SEARCH_FILTERS[field]
    ) {
      body[field] = searchFilters[field] as ListOffersQueryModel[typeof field]
    }
  })
  return body
}
