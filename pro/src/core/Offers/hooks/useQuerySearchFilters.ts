import { useMemo } from 'react'
import { useLocation } from 'react-router-dom'

import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { parse } from 'utils/query-string'
import { translateQueryParamsToApiParams } from 'utils/translate'

import { SearchFiltersParams } from '../types'

export const useQuerySearchFilters = (): SearchFiltersParams => {
  const { search } = useLocation()

  const urlSearchFilters: SearchFiltersParams = useMemo(() => {
    const queryParams = parse(search)
    const translatedQuery = translateQueryParamsToApiParams({
      ...queryParams,
    })

    const urlFilters = {
      ...DEFAULT_SEARCH_FILTERS,
      ...translatedQuery,
    }

    // Convert page type to number
    urlFilters.page =
      typeof urlFilters.page === 'string'
        ? parseInt(urlFilters.page)
        : urlFilters.page

    return urlFilters
  }, [search])

  return urlSearchFilters
}
